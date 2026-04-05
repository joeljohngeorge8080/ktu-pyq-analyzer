from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Any

class QuestionCreate(BaseModel):
    paper_id: int
    module: int
    type: str
    question_number: Optional[str] = None
    tags: Optional[List[str]] = []
    page_number: Optional[int] = 1
    crop_coords: Optional[dict] = None
    notes: Optional[str] = None

    @field_validator("module")
    @classmethod
    def module_range(cls, v):
        if v not in range(1, 6):
            raise ValueError("Module must be 1–5")
        return v

    @field_validator("type")
    @classmethod
    def type_valid(cls, v):
        if v not in ("short", "long"):
            raise ValueError("Type must be 'short' or 'long'")
        return v

class QuestionUpdate(BaseModel):
    module: Optional[int] = None
    type: Optional[str] = None
    question_number: Optional[str] = None

    @field_validator("module")
    @classmethod
    def module_range(cls, v):
        if v is not None and v not in range(1, 6):
            raise ValueError("Module must be 1–5")
        return v

    @field_validator("type")
    @classmethod
    def type_valid(cls, v):
        if v is not None and v not in ("short", "long"):
            raise ValueError("Type must be 'short' or 'long'")
        return v


class QuestionOut(BaseModel):
    id: int
    paper_id: int
    module: int
    type: str
    question_number: Optional[str]
    image_path: str
    tags: Optional[List[Any]]
    page_number: int
    crop_coords: Optional[dict]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
