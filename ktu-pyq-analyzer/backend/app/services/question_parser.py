import re
import os
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from PIL import Image

from app.models.paper import Paper
from app.models.question import Question
from app.config import settings

logger = logging.getLogger(__name__)

def parse_paper(db: Session, paper_id: int):
    """
    Processes a paper: extracts images, detects question blocks, and creates crops.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise ValueError("Paper not found")

    import pytesseract
    try:
        from pdf2image import convert_from_path
    except ImportError:
        logger.error("pdf2image not installed")
        raise

    abs_path = str(settings.upload_path / paper.file_path)
    
    # 1. Provide images per page
    images = []
    if paper.file_type == "pdf":
        try:
            images = convert_from_path(abs_path, dpi=200)
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise
    else:
        try:
            images = [Image.open(abs_path)]
        except Exception as e:
            logger.error(f"Failed to open image: {e}")
            raise

    # 2. Iterate pages, find questions
    for page_idx, img in enumerate(images):
        page_num = page_idx + 1
        
        # We will do a simple OCR to get words and their boxes
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        n_boxes = len(data['text'])
        questions_on_page = []
        current_question = None
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            if text == "" or conf < 0:
                continue
                
            # Regex: match "1.", "12."
            match = re.match(r'^(\d+)\.$', text)
            if match:
                q_num = match.group(1)
                
                # Assume a question number starts near the left margin
                # But to avoid deep heuristic failures, we just rely on regex
                
                # If we had a current question, finish it
                if current_question:
                    questions_on_page.append(current_question)

                current_question = {
                    "question_number": int(q_num),
                    "text_blocks": [],
                    "x_min": data['left'][i],
                    "y_min": data['top'][i],
                    "x_max": data['left'][i] + data['width'][i],
                    "y_max": data['top'][i] + data['height'][i],
                }
            
            # If we are inside a question block, expand its bounding box
            elif current_question:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                
                # But wait, footers/page numbers might pollute it. 
                # Let's say if y is too far down, we ignore. 
                # Actually, just expand bounding box.
                if y > current_question["y_max"] + 200:
                    pass # Probably a stray word far below, but we'll include it.
                    
                current_question["x_min"] = min(current_question["x_min"], x)
                current_question["y_min"] = min(current_question["y_min"], y)
                current_question["x_max"] = max(current_question["x_max"], x + w)
                current_question["y_max"] = max(current_question["y_max"], y + h)
                current_question["text_blocks"].append(text)
                
        if current_question:
            questions_on_page.append(current_question)
            
        # 3. Crop and Save Output
        for q in questions_on_page:
            q_num = q["question_number"]
            # Detect section and module
            q_type = "short"
            module = 1
            if q_num <= 10:
                q_type = "short"
                module = ((q_num - 1) // 2) + 1
            else:
                q_type = "long"
                module = ((q_num - 11) // 2) + 1
            
            # Ensure module is within 1-5
            module = max(1, min(5, module))

            # Crop image
            # Provide some padding
            pad = 20
            x1 = max(0, q["x_min"] - pad)
            y1 = max(0, q["y_min"] - pad)
            x2 = min(img.width, q["x_max"] + pad)
            y2 = min(img.height, q["y_max"] + pad)
            
            # only crop if height > padding etc.
            if y2 <= y1 or x2 <= x1:
                continue

            crop = img.crop((x1, y1, x2, y2))
            
            # Save cropped image
            crop_filename = f"paper_{paper.id}_q{q_num}_{uuid.uuid4().hex[:6]}.png"
            crop_rel_path = f"questions/{crop_filename}"
            crop_abs_path = settings.upload_path / "questions" / crop_filename
            crop_abs_path.parent.mkdir(parents=True, exist_ok=True)
            crop.save(str(crop_abs_path), "PNG")
            
            # DB entry
            new_q = Question(
                paper_id=paper.id,
                module=module,
                type=q_type,
                question_number=str(q_num),
                image_path=crop_rel_path,
                page_number=page_num,
                crop_coords={"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1},
                tags=[]
            )
            db.add(new_q)
            
    db.commit()
    return True
