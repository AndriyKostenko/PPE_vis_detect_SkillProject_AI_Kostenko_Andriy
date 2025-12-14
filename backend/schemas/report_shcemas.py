from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, PositiveInt, field_validator
from pydantic.fields import Field
from schemas.detect_schemas import DetectionSchema, DetectionSummarySchema


class DetectionRequestSchema(BaseModel):
    image_id: str = Field(..., description="Unique identifier for the image")
    timestamp: datetime = Field(..., description="Timestamp of the detection request")
    summary: DetectionSummarySchema = Field(..., description="Summary of detections")   
    detections: list[DetectionSchema] = Field(..., description="List of detections")
    annotated_image: str = Field(..., description="Base64 encoded annotated image")
    

class ReportResponseSchema(BaseModel):
    status: str = Field(..., description="Status message of the PDF report generation")
    report_url: str = Field(..., description="URL to the generated PDF report")