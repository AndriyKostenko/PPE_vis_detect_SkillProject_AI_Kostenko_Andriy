from fastapi import APIRouter, UploadFile, File, HTTPException, status

from schemas.report_shcemas import DetectionRequestSchema
from pdf_report_generator import report_generator

report_router = APIRouter()

# TODO: Create a service to generate PDF report using PDFReportGenerator
@report_router.post("/report",
                     summary="Generate PDF report from detections and annotated image",
                     response_description="PDF report generation status",
                     status_code=status.HTTP_201_CREATED)
def generate_the_report(data: DetectionRequestSchema):  
    try:
        pdf_path = report_generator.generate_report(
            detections=data.detections,
            annotated_image_base64=data.annotated_image
        )
        return {"message": "PDF report generated successfully", "pdf_path": pdf_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {e}")
        