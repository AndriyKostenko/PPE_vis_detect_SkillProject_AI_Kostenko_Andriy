from fastapi import APIRouter, UploadFile, File, HTTPException, status

from schemas.report_shcemas import DetectionRequestSchema
from pdf_report_generator import report_generator
from schemas.report_shcemas import ReportResponseSchema


report_router = APIRouter(tags=["PDF Report endpoints"])


# TODO: Create a Service to generate PDF report using PDFReportGenerator
# TODO: Performance can be suff. icreased using mulytiprocessing or Background Tasks
@report_router.post("/report",
                     summary="Generate PDF report from detections and annotated image",
                     response_description="PDF report generation status",
                     status_code=status.HTTP_201_CREATED,
                     response_model=ReportResponseSchema)
async def generate_the_report(data: DetectionRequestSchema):  
    try:
        pdf_path = report_generator.generate_report(
            image_id=data.image_id,
            timestamp=data.timestamp,
            summary=data.summary,
            detections=data.detections,
            annotated_image_base64=data.annotated_image
        )
        return ReportResponseSchema(
            status="PDF report generated successfully",
            report_url=str(pdf_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {e}")
        