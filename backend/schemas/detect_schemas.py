from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID

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
    
class DetectionResponseSchema(BaseModel):
    success: bool = Field(..., description="Indicates if detection was successful")
    message: str = Field(..., description="Detection result message")
    annotated_image: str = Field(..., description="Base64 encoded annotated image")
    
    model_config = ConfigDict(from_attributes=True)
    