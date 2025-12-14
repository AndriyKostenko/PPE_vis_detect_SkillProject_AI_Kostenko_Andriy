from pathlib import Path
from typing import Optional

from ultralytics import YOLO
import torch
import cv2  

from logger import logger, Logger
from settings import Settings, settings


class InferenceManager:
    """
    Manages the inference process using a pre-trained YOLO model.
    """
    def __init__(self, model_path: str, settings: Settings, logger: Logger):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            logger.error(f"Model path {self.model_path} does not exist.")
            raise FileNotFoundError(f"Model path {self.model_path} does not exist.")
        
        self.settings = settings
        self.logger = logger
        self.model = YOLO(self.model_path)
        self.device = self._detect_device_for_training()
        self.classes = self.model.names
        self.confidence_threshold = self.settings.CONFIDENCE_THRESHOLD
        self.iou_threshold = self.settings.IOU_THRESHOLD
        
        self.annotated_image_save_path = settings.BASE_DIR / "inference_results"
        self.annotated_image_save_path.mkdir(parents=True, exist_ok=True)
        
    def _detect_device_for_training(self) -> str:
        """Detect if CUDA is available for training."""
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.logger.info(f"Using device for training: {device}")
        return device
    
    def predict(self, image_path: str):
        """Run inference on the given image."""
        self.logger.info(f"Running inference on image: {image_path}")
        results = self.model.predict(source=image_path, device=self.device, conf=self.confidence_threshold, iou=self.iou_threshold)
        self.logger.info("Inference completed.")
        return results
    
    def annotate_image_and_save(self, image_path: str) -> Path:
        """Annotate the image with detection results and save it."""
        results = self.predict(image_path)
        annotated_image = results[0].plot()
        
        input_filename = Path(image_path).stem
        output_filename = f"{input_filename}_annotated.jpg"
        output_path = str(self.annotated_image_save_path / output_filename)
        cv2.imwrite(output_path, annotated_image)
        self.logger.info(f"Annotated image saved to: {output_path}")
        return output_path
    
    def get_detections(self, image_path: str):
        """Get detection results in a structured format."""
        results = self.predict(image_path)
        detections = []
        violations = 0
        complaints = 0
        
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()  # [x_min, y_min, x_max, y_max]
                detections.append({
                    "class": self.classes[cls_id],
                    "confidence": round(confidence, 2),
                    "bbox": bbox
                })
                
                if self.classes[cls_id] == "head":
                    violations += 1
                elif self.classes[cls_id] == "helmet":
                    complaints += 1
        return detections, violations, complaints


inference_manager = InferenceManager(model_path=str(settings.BASE_DIR / "trained_models" / "best_ppe_model.pt"), 
                                     settings=settings, 
                                     logger=logger)
    
    
if __name__ == "__main__":
    model_path = settings.BASE_DIR / "trained_models" / "best_ppe_model.pt"
    test_image_path = settings.BASE_DIR / "uploads" / "test_img_2.jpeg"
    
    inference_manager = InferenceManager(model_path=str(model_path), settings=settings, logger=logger)
    #inference_manager.annotate_image_and_save(image_path=str(test_image_path))
    print(inference_manager.get_detections(image_path=str(test_image_path)))
    print("Model classes: ", inference_manager.classes)
    
        