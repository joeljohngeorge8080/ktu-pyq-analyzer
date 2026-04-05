from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class SubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Subject name cannot be empty")
        return v.strip()

class SubjectOut(BaseModel):
    id: int
    name: str
    code: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
