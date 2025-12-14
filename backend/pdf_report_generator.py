from uuid import uuid4
import io
import base64
import os
from pathlib import Path
from datetime import datetime

import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from settings import Settings, settings
from logger import Logger, logger
from schemas.detect_schemas import DetectionResponseSchema


class PDFReportGenerator:
    """Service to generate PDF reports from detection data and annotated images."""
    def __init__(self, settings: Settings, logger: Logger):
        self.settings = settings
        self.logger = logger
        self.output_path = Path(self.settings.PDF_REPORTS_DIR)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def _generate_unique_filename() -> str:
        return f"report_{uuid4().hex}.pdf"
    
    def _draw_wrapped_text(self, c, text, x, y, max_width, font_name="Helvetica", font_size=12, line_height=20):
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if stringWidth(test_line, font_name, font_size) <= max_width:
                line = test_line
            else:
                c.drawString(x, y, line)
                y -= line_height
                line = word
        if line:
            c.drawString(x, y, line)
            y -= line_height
        return y
        
    def generate_report(self, detections: list, annotated_image_base64: str, summary, image_id: str, timestamp: datetime) -> Path:
        try:  
            filename = self._generate_unique_filename()
            output_path = self.output_path / filename
            width, height = letter
            
            total_detections = len(detections)
            image_id = image_id
            timestamp_formatted = datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S")
            violations = summary.no_helmet_count
            complaints = summary.helmet_count
            
            c = canvas.Canvas(str(output_path), pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(30, height - 30, "PPE Safety Incident Report")

            # Add image ID and timestamp
            y_position = height - 60
            c.drawString(30, y_position, f"Image ID: {image_id}")
            y_position -= 20
            c.drawString(30, y_position, f"Timestamp: {timestamp_formatted}")

            # Add detection summary
            y_position -= 20
            c.drawString(30, y_position, f"Total Detections: {total_detections}")
            y_position -= 20
            c.drawString(30, y_position, f"Violations: {violations}")
            y_position -= 20
            c.drawString(30, y_position, f"Complaints: {complaints}")
            y_position -= 30  # Space before detections list
            line_height = 20
            bottom_margin = 60
            left_margin = 30
            max_text_width = width - left_margin * 2

            for detection in detections:
                if y_position < bottom_margin:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = height - 30
                detection_text = f"Class: {detection.class_}, Confidence: {detection.confidence:.2f}, BBox: {detection.bbox}"
                y_position = self._draw_wrapped_text(
                    c, detection_text, left_margin, y_position, max_text_width, "Helvetica", 12, line_height
                )

            # Ensure enough space for the image, otherwise move to new page
            image_height = 300
            image_width = 500
            if y_position - image_height < bottom_margin:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 30

            # Decode the base64 image
            image_data = base64.b64decode(annotated_image_base64)
            image_stream = io.BytesIO(image_data)
            image = ImageReader(image_stream)

            c.drawImage(image, left_margin, y_position - image_height, width=image_width, height=image_height)

            c.save()
            self.logger.info(f"PDF report generated at: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to generate PDF report: {e}")
            raise
        
    
report_generator = PDFReportGenerator(settings=settings, logger=logger)
    

if __name__ == "__main__":
    pass
    #report_generator = PDFReportGenerator(settings=settings, logger=logger)
    