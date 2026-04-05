"""
OCR Service — extracts text blocks with bounding boxes from images.
Uses Tesseract with word/line-level granularity.
Returns structured, position-aware text blocks sorted top→bottom, left→right.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    text: str
    x: int
    y: int
    w: int
    h: int
    conf: int = 0
    page: int = 1

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @property
    def cx(self):
        return self.x + self.w // 2

    @property
    def cy(self):
        return self.y + self.h // 2


@dataclass
class PageBlocks:
    page_num: int
    image: Image.Image
    blocks: List[TextBlock] = field(default_factory=list)
    width: int = 0
    height: int = 0


def extract_blocks_from_image(img: Image.Image, page_num: int = 1, min_conf: int = 20) -> PageBlocks:
    """
    Run Tesseract on a PIL image and return all text blocks with positions.
    Blocks are sorted top→bottom, then left→right (reading order).
    """
    try:
        import pytesseract
    except ImportError:
        raise RuntimeError("pytesseract not installed")

    result = PageBlocks(page_num=page_num, image=img, width=img.width, height=img.height)

    # Use word-level output for fine-grained bounding boxes
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang='eng')

    n = len(data['text'])
    for i in range(n):
        raw = data['text'][i]
        if not raw or not raw.strip():
            continue
        conf = int(data['conf'][i])
        if conf < min_conf:
            continue

        block = TextBlock(
            text=raw.strip(),
            x=int(data['left'][i]),
            y=int(data['top'][i]),
            w=int(data['width'][i]),
            h=int(data['height'][i]),
            conf=conf,
            page=page_num,
        )
        result.blocks.append(block)

    # Sort reading order: top→bottom (with 10px row tolerance), then left→right
    result.blocks.sort(key=lambda b: (b.y // 10, b.x))

    logger.debug(f"Page {page_num}: extracted {len(result.blocks)} text blocks")
    return result


def blocks_to_lines(blocks: List[TextBlock], row_gap: int = 8) -> List[List[TextBlock]]:
    """
    Group individual word blocks into lines based on vertical proximity.
    Returns list of lines, each line is a list of TextBlock sorted left→right.
    """
    if not blocks:
        return []

    sorted_blocks = sorted(blocks, key=lambda b: (b.y, b.x))
    lines: List[List[TextBlock]] = []
    current_line: List[TextBlock] = [sorted_blocks[0]]

    for block in sorted_blocks[1:]:
        last = current_line[-1]
        # Same line if vertical overlap or close enough
        if abs(block.y - last.y) <= row_gap or (block.y < last.y2 and block.y2 > last.y):
            current_line.append(block)
        else:
            lines.append(sorted(current_line, key=lambda b: b.x))
            current_line = [block]

    if current_line:
        lines.append(sorted(current_line, key=lambda b: b.x))

    return lines


def line_text(line: List[TextBlock]) -> str:
    """Join all text in a line."""
    return " ".join(b.text for b in line).strip()


def find_text_in_blocks(blocks: List[TextBlock], pattern: str,
                         flags=re.IGNORECASE) -> Optional[TextBlock]:
    """Find first block matching a regex pattern."""
    rx = re.compile(pattern, flags)
    for b in blocks:
        if rx.search(b.text):
            return b
    return None


def find_all_matching(blocks: List[TextBlock], pattern: str,
                       flags=re.IGNORECASE) -> List[TextBlock]:
    """Find all blocks matching a regex pattern."""
    rx = re.compile(pattern, flags)
    return [b for b in blocks if rx.search(b.text)]
