from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, PositiveInt, field_validator
from pydantic.fields import Field
from schemas.detect_schemas import DetectionSchema


class DetectionRequestSchema(BaseModel):
    detections: list[DetectionSchema] = Field(..., description="List of detections")
    annotated_image: str = Field(..., description="Base64 encoded annotated image")