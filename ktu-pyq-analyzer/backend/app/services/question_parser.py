"""
KTU Question Paper Parser — 3-Stage Layout-Aware System

STAGE 1: Text + Position Extraction
STAGE 2: Section Detection (PART A / PART B / Module headers)
STAGE 3: Question Detection with spatial grouping

KTU Paper Structure:
  PAGE 1:
    PART A — Questions 1–10 (Short Answers, 2 marks each)
  PAGES 1–3:
    PART B — Questions 11–20 (Long Answers, 14 marks each)
      Module I   → Q11, Q12
      Module II  → Q13, Q14
      Module III → Q15, Q16
      Module IV  → Q17, Q18
      Module V   → Q19, Q20

Module mapping (fixed by KTU convention):
  Q11,Q12 → Module 1
  Q13,Q14 → Module 2
  Q15,Q16 → Module 3
  Q17,Q18 → Module 4
  Q19,Q20 → Module 5
"""

import logging
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from PIL import Image
from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.models.question import Question
from app.config import settings
from app.services.ocr_service import (
    TextBlock, PageBlocks,
    extract_blocks_from_image, blocks_to_lines, line_text,
    find_text_in_blocks, find_all_matching,
)

logger = logging.getLogger(__name__)

# ─── Module mapping by question number ────────────────────────────────────────
MODULE_MAP: Dict[int, int] = {}
for _q in range(11, 13): MODULE_MAP[_q] = 1
for _q in range(13, 15): MODULE_MAP[_q] = 2
for _q in range(15, 17): MODULE_MAP[_q] = 3
for _q in range(17, 19): MODULE_MAP[_q] = 4
for _q in range(19, 21): MODULE_MAP[_q] = 5

# Module header patterns
MODULE_HEADER_PATTERNS = [
    r'\bmodule\s*[I1](?![IV\d])\b',   # Module I / Module 1
    r'\bmodule\s*I{2}\b',              # Module II
    r'\bmodule\s*II{2}\b',             # Module III
    r'\bmodule\s*IV\b',                # Module IV
    r'\bmodule\s*V(?!I)\b',            # Module V
    r'\bmodule\s*[2-5]\b',             # Module 2–5
]

MODULE_ROMAN = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
}


@dataclass
class DetectedQuestion:
    question_number: int
    module: int
    q_type: str           # "short" or "long"
    page: int
    y_start: int
    y_end: int
    x_start: int
    x_end: int
    subparts: List[str] = field(default_factory=list)
    image_path: str = ""
    crop_coords: dict = field(default_factory=dict)


# ─── Stage 1: Load pages ──────────────────────────────────────────────────────

def load_pages(paper: Paper) -> List[PageBlocks]:
    """Convert paper file (PDF or image) into list of PageBlocks with OCR data."""
    abs_path = str(settings.upload_path / paper.file_path)

    if paper.file_type == "pdf":
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(abs_path, dpi=200)
            logger.info(f"PDF → {len(images)} pages at 200 DPI")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise
    else:
        images = [Image.open(abs_path)]
        logger.info("Single image loaded")

    pages = []
    for i, img in enumerate(images):
        logger.info(f"  OCR page {i+1}/{len(images)} ({img.width}×{img.height}px)…")
        page_blocks = extract_blocks_from_image(img, page_num=i + 1, min_conf=20)
        pages.append(page_blocks)
        logger.debug(f"  Page {i+1}: {len(page_blocks.blocks)} blocks extracted")

    return pages


# ─── Stage 2: Section Detection ───────────────────────────────────────────────

@dataclass
class SectionBoundary:
    label: str          # "PART_A", "PART_B", "MODULE_1" .. "MODULE_5"
    page: int
    y: int              # y-position of the header block
    module_num: Optional[int] = None


def detect_sections(pages: List[PageBlocks]) -> List[SectionBoundary]:
    """
    Scan all pages and find PART A, PART B, and Module headers.
    Returns list of SectionBoundary sorted by (page, y).
    """
    sections: List[SectionBoundary] = []

    part_a_rx = re.compile(r'part\s*[A]', re.IGNORECASE)
    part_b_rx = re.compile(r'part\s*[B]', re.IGNORECASE)
    module_rx = re.compile(
        r'module\s*(I{1,3}V?|IV|V|[1-5])\b', re.IGNORECASE
    )

    for pb in pages:
        lines = blocks_to_lines(pb.blocks)
        for line in lines:
            text = line_text(line)
            y = min(b.y for b in line)

            if part_a_rx.search(text) and len(text) < 30:
                sections.append(SectionBoundary("PART_A", pb.page_num, y))
                logger.info(f"  ✓ PART A detected → page {pb.page_num}, y={y}")

            elif part_b_rx.search(text) and len(text) < 30:
                sections.append(SectionBoundary("PART_B", pb.page_num, y))
                logger.info(f"  ✓ PART B detected → page {pb.page_num}, y={y}")

            else:
                m = module_rx.search(text)
                if m and len(text) < 40:
                    roman = m.group(1).upper()
                    mod_num = MODULE_ROMAN.get(roman, None)
                    if mod_num:
                        label = f"MODULE_{mod_num}"
                        sections.append(SectionBoundary(label, pb.page_num, y, mod_num))
                        logger.info(f"  ✓ Module {mod_num} header → page {pb.page_num}, y={y}")

    # Sort by page then y
    sections.sort(key=lambda s: (s.page, s.y))
    return sections


# ─── Stage 3A: Short question detection (PART A) ──────────────────────────────

def detect_short_questions(pages: List[PageBlocks],
                            part_a_page: int, part_a_y: int,
                            part_b_page: int, part_b_y: int) -> List[DetectedQuestion]:
    """
    Detect questions 1–10 in PART A region.
    Strategy:
    - Collect all blocks between PART A header and PART B header
    - Find blocks whose text is a standalone digit 1–10
    - Group subsequent text blocks as the question body
    - Crop from q_number y to next_q_number y
    """
    q_num_rx = re.compile(r'^(\d{1,2})[.\):]?$')

    # Gather all blocks in PART A zone (across pages)
    zone_blocks: List[Tuple[int, TextBlock]] = []  # (page_num, block)
    for pb in pages:
        for b in pb.blocks:
            in_zone = False
            if pb.page_num == part_a_page and pb.page_num == part_b_page:
                in_zone = part_a_y <= b.y < part_b_y
            elif pb.page_num == part_a_page:
                in_zone = b.y >= part_a_y
            elif pb.page_num == part_b_page:
                in_zone = b.y < part_b_y
            elif part_a_page < pb.page_num < part_b_page:
                in_zone = True
            if in_zone:
                zone_blocks.append((pb.page_num, b))

    # Sort by page→y→x
    zone_blocks.sort(key=lambda t: (t[0], t[1].y, t[1].x))

    # Find question number anchors (standalone 1–10 near left margin)
    page_widths = {pb.page_num: pb.width for pb in pages}
    anchors: List[Tuple[int, int, TextBlock]] = []  # (q_num, page, block)

    for (pg, b) in zone_blocks:
        m = q_num_rx.match(b.text)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 10:
                pw = page_widths.get(pg, 2000)
                # Must be in left 20% of page (question numbers are left-aligned)
                if b.x < pw * 0.25:
                    # Avoid duplicates (same number already captured)
                    if not any(a[0] == n for a in anchors):
                        anchors.append((n, pg, b))
                        logger.debug(f"    Short Q{n} anchor: page={pg} y={b.y} x={b.x}")

    anchors.sort(key=lambda a: (a[1], a[2].y))

    detected: List[DetectedQuestion] = []
    page_images = {pb.page_num: pb for pb in pages}

    for idx, (q_num, q_page, q_block) in enumerate(anchors):
        # Determine end boundary
        if idx + 1 < len(anchors):
            next_q_num, next_q_page, next_q_block = anchors[idx + 1]
            end_page = next_q_page
            end_y = next_q_block.y - 5
        else:
            end_page = q_page
            end_y = page_images[q_page].height if q_page in page_images else 9999

        # Collect blocks in this question's region
        q_blocks = [
            b for (pg, b) in zone_blocks
            if pg == q_page and q_block.y <= b.y < end_y
        ]

        if not q_blocks:
            q_blocks = [q_block]

        x1 = max(0, min(b.x for b in q_blocks) - 5)
        y1 = max(0, q_block.y - 5)
        x2 = min(page_images.get(q_page, PageBlocks(q_page, None)).width or 9999,
                 max(b.x2 for b in q_blocks) + 10)
        y2 = min(page_images.get(q_page, PageBlocks(q_page, None)).height or 9999,
                 max(b.y2 for b in q_blocks) + 10)

        dq = DetectedQuestion(
            question_number=q_num,
            module=1,   # PART A questions belong to the overall paper, module=1 by convention
            q_type="short",
            page=q_page,
            y_start=y1, y_end=y2,
            x_start=x1, x_end=x2,
        )
        detected.append(dq)
        logger.info(f"  SHORT Q{q_num} → page={q_page} bbox=({x1},{y1},{x2},{y2})")

    return detected


# ─── Stage 3B: Long question detection (PART B) ───────────────────────────────

def detect_long_questions(pages: List[PageBlocks],
                           sections: List[SectionBoundary]) -> List[DetectedQuestion]:
    """
    Detect questions 11–20 in PART B region, grouped by module.
    Strategy per module:
    - Find the module header boundary
    - Scan until next module header (or end of document)
    - Within that zone, find standalone 2-digit numbers 11–20
    - Group each question until next question anchor
    - Detect subparts (a), (b) within each question
    """
    q_num_rx = re.compile(r'^(\d{2})[.\):]?$')
    subpart_rx = re.compile(r'^[a-zA-Z][.\):]$')

    # Build module zones: (module_num, start_page, start_y, end_page, end_y)
    module_sections = [s for s in sections if s.label.startswith("MODULE_")]

    if not module_sections:
        logger.warning("No module headers detected — will try to infer from question numbers")

    page_images = {pb.page_num: pb for pb in pages}
    page_widths = {pb.page_num: pb.width for pb in pages}

    # Collect ALL blocks from PART B onward
    part_b = next((s for s in sections if s.label == "PART_B"), None)
    if not part_b:
        logger.warning("PART B not detected — scanning all pages for long questions")
        part_b_page, part_b_y = 1, 0
    else:
        part_b_page, part_b_y = part_b.page, part_b.y

    zone_blocks: List[Tuple[int, TextBlock]] = []
    for pb in pages:
        for b in pb.blocks:
            if (pb.page_num > part_b_page or
                    (pb.page_num == part_b_page and b.y >= part_b_y)):
                zone_blocks.append((pb.page_num, b))

    zone_blocks.sort(key=lambda t: (t[0], t[1].y, t[1].x))

    # Find all question number anchors (11–20) in left margin
    anchors: List[Tuple[int, int, TextBlock]] = []
    for (pg, b) in zone_blocks:
        m = q_num_rx.match(b.text)
        if m:
            n = int(m.group(1))
            if 11 <= n <= 20:
                pw = page_widths.get(pg, 2000)
                if b.x < pw * 0.25:
                    if not any(a[0] == n for a in anchors):
                        anchors.append((n, pg, b))
                        logger.debug(f"    Long Q{n} anchor: page={pg} y={b.y}")

    anchors.sort(key=lambda a: (a[1], a[2].y))

    detected: List[DetectedQuestion] = []

    for idx, (q_num, q_page, q_block) in enumerate(anchors):
        # Boundary: next question anchor
        if idx + 1 < len(anchors):
            _, next_pg, next_blk = anchors[idx + 1]
            end_page, end_y = next_pg, next_blk.y - 5
        else:
            end_page = q_page
            end_y = page_images[q_page].height if q_page in page_images else 9999

        # Collect blocks for this question
        q_blocks = [
            b for (pg, b) in zone_blocks
            if pg == q_page and q_block.y <= b.y < end_y
        ]
        if not q_blocks:
            q_blocks = [q_block]

        # Detect subparts
        subparts = []
        for b in q_blocks:
            if subpart_rx.match(b.text):
                subparts.append(b.text.rstrip('.):').lower())

        pb_info = page_images.get(q_page)
        x1 = max(0, min(b.x for b in q_blocks) - 5)
        y1 = max(0, q_block.y - 5)
        x2 = min(pb_info.width if pb_info else 9999, max(b.x2 for b in q_blocks) + 10)
        y2 = min(pb_info.height if pb_info else 9999, max(b.y2 for b in q_blocks) + 10)

        module = MODULE_MAP.get(q_num, 1)

        dq = DetectedQuestion(
            question_number=q_num,
            module=module,
            q_type="long",
            page=q_page,
            y_start=y1, y_end=y2,
            x_start=x1, x_end=x2,
            subparts=subparts,
        )
        detected.append(dq)
        logger.info(
            f"  LONG Q{q_num} → Module {module} | page={q_page} "
            f"bbox=({x1},{y1},{x2},{y2}) subparts={subparts}"
        )

    return detected


# ─── Stage 4: Crop + Save ─────────────────────────────────────────────────────

def crop_and_save(dq: DetectedQuestion, pages: List[PageBlocks]) -> str:
    """Crop the question region from the page image and save it. Returns relative path."""
    pb = next((p for p in pages if p.page_num == dq.page), None)
    if pb is None or pb.image is None:
        raise ValueError(f"Page {dq.page} image not available")

    img = pb.image
    iw, ih = img.size

    x1 = max(0, dq.x_start)
    y1 = max(0, dq.y_start)
    x2 = min(iw, dq.x_end)
    y2 = min(ih, dq.y_end)

    if x2 <= x1 or y2 <= y1:
        logger.warning(f"Q{dq.question_number}: degenerate crop bbox, using full width")
        x1, x2 = 0, iw
        y2 = min(ih, y1 + 200)

    cropped = img.crop((x1, y1, x2, y2))

    filename = f"paper_{dq.question_number}_q{dq.question_number}_{uuid.uuid4().hex[:8]}.png"
    rel_path = f"questions/{filename}"
    abs_path = settings.upload_path / "questions" / filename
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(str(abs_path), "PNG")

    dq.image_path = rel_path
    dq.crop_coords = {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1}
    return rel_path


# ─── Main entrypoint ──────────────────────────────────────────────────────────

def parse_paper(db: Session, paper_id: int) -> bool:
    """
    Full 3-stage parsing pipeline.
    Returns True on success.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise ValueError(f"Paper {paper_id} not found")

    logger.info(f"=== Parsing paper {paper_id}: {paper.original_filename} ===")

    # ── Stage 1: Extract OCR blocks from all pages
    logger.info("STAGE 1: OCR Extraction")
    pages = load_pages(paper)

    # ── Stage 2: Detect sections
    logger.info("STAGE 2: Section Detection")
    sections = detect_sections(pages)

    part_a = next((s for s in sections if s.label == "PART_A"), None)
    part_b = next((s for s in sections if s.label == "PART_B"), None)

    if not part_a:
        logger.warning("PART A not found — defaulting to page 1, y=0")
        part_a = type('S', (), {'page': 1, 'y': 0})()
    if not part_b:
        logger.warning("PART B not found — defaulting to page 1, y=half")
        pb0 = pages[0]
        part_b = type('S', (), {'page': 1, 'y': pb0.height // 2})()

    logger.info(f"  PART A: page={part_a.page} y={part_a.y}")
    logger.info(f"  PART B: page={part_b.page} y={part_b.y}")

    # ── Stage 3A: Short questions
    logger.info("STAGE 3A: Short Question Detection")
    short_qs = detect_short_questions(
        pages,
        part_a_page=part_a.page, part_a_y=part_a.y,
        part_b_page=part_b.page, part_b_y=part_b.y,
    )

    # ── Stage 3B: Long questions
    logger.info("STAGE 3B: Long Question Detection")
    long_qs = detect_long_questions(pages, sections)

    all_questions = short_qs + long_qs
    all_questions.sort(key=lambda q: q.question_number)

    # ── Debug summary
    logger.info("\n=== DETECTION SUMMARY ===")
    for dq in all_questions:
        logger.info(
            f"  Q{dq.question_number:>2} → {dq.q_type.upper():<5} → Module {dq.module}"
            + (f" → subparts: {dq.subparts}" if dq.subparts else "")
        )

    if not all_questions:
        logger.warning("No questions detected. Check OCR quality or paper structure.")
        return False

    # ── Stage 4: Crop, save, persist
    logger.info("STAGE 4: Cropping and Saving")
    saved_count = 0

    # Remove previously auto-parsed questions for this paper
    db.query(Question).filter(Question.paper_id == paper_id).delete()
    db.commit()

    for dq in all_questions:
        try:
            rel_path = crop_and_save(dq, pages)
        except Exception as e:
            logger.error(f"  ✗ Q{dq.question_number}: crop failed — {e}")
            continue

        q_obj = Question(
            paper_id=paper_id,
            module=dq.module,
            type=dq.q_type,
            question_number=str(dq.question_number),
            image_path=rel_path,
            tags=[],
            page_number=dq.page,
            crop_coords=dq.crop_coords,
            notes=f"subparts: {','.join(dq.subparts)}" if dq.subparts else None,
        )
        db.add(q_obj)
        saved_count += 1
        logger.info(f"  ✓ Q{dq.question_number} saved → {rel_path}")

    db.commit()
    logger.info(f"=== Done: {saved_count}/{len(all_questions)} questions saved ===")
    return saved_count > 0
