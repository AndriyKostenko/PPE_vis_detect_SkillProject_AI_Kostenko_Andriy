from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, PositiveInt, field_validator
from pydantic.fields import Field


class ImageUploadSchema(BaseModel):
    filename: str = Field(..., description="The name of the uploaded image file")
    content_type: str = Field(..., description="The MIME type of the uploaded image file")
    size: PositiveInt = Field(..., gt=0, le=2*1024*1024, description="The size of the uploaded image file in bytes (max 2MB)")
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v) -> str:
        """Validate that the content type is one of the allowed image types."""
        alloweed_types = ("image/jpeg", "image/jpg", "image/png")
        if v not in alloweed_types:
            raise ValueError(f"Unsupported file type: {v}. Allowed types are: {', '.join(alloweed_types)}")
        return v
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v) -> str:
        """Validate that the filename has a proper image extension."""
        allowed_extensions = (".jpeg", ".jpg", ".png")
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f"Unsupported file extension in filename: {v}. Allowed extensions are: {', '.join(allowed_extensions)}")
        return v
    
    
    model_config = ConfigDict(from_attributes=True)
    
class DetectionSchema(BaseModel):
    class_: str = Field(..., alias="class", description="Detected class label")
    confidence: float = Field(..., description="Confidence score of the detection")
    bbox: list[float] = Field(..., description="Bounding box coordinates [x_min, y_min, x_max, y_max]")

class DetectionResponseSchema(BaseModel):
    detections: list[DetectionSchema] = Field(..., description="List of detections")
    annotated_image: str 
    