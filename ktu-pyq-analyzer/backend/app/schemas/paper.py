from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaperOut(BaseModel):
    id: int
    subject_id: int
    year: int
    exam_type: Optional[str]
    file_path: str
    original_filename: str
    file_type: str
    page_count: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}
