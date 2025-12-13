from pathlib import Path

from ultralytics import YOLO
import torch

from settings import Settings, settings
from logger import Logger, logger


class YOLOmodelTrainer:
    def __init__(self, logger: Logger, settings: Settings):
        self.logger = logger
        self.settings = settings
        
        self.dataset_yaml_path = self.settings.DATASET_YAML_PATH
        self.dataset_path = self.settings.DATASET_PATH
        
        self.logger.info(f"Training dataset YAML: {self.dataset_yaml_path}")
        self.logger.info(f"Training dataset folder: {self.dataset_path}")
        
        if not self.dataset_yaml_path.exists():
            self.logger.error(f"Dataset YAML not found: {self.dataset_yaml_path}")
            raise ValueError(f"Training dataset YAML not found: {self.dataset_yaml_path}")
        
        if not self.dataset_path.exists():
            self.logger.error(f"Dataset folder not found: {self.dataset_path}")
            raise ValueError(f"Training dataset folder not found: {self.dataset_path}")
    
        self.model = YOLO(self.settings.MODEL_NAME_AND_SIZE)
        self.images_for_training = len(list(self.dataset_path.glob('train/images/*.jpg')))
        self.images_for_validation = len(list(self.dataset_path.glob('valid/images/*.jpg')))
        self.batch_size = self.settings.BATCH_SIZE
        self.number_of_epochs = self.settings.NUMBER_OF_EPOCHS
        self.model_image_size = self.settings.MODEL_IMG_SIZE
        self.device_for_training = self._detect_device_for_training()
        
    def _detect_device_for_training(self) -> str:
        """Detect if CUDA is available for training."""
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.logger.info(f"Using device for training: {device}")
        return device

    def train(self):
        """Train the YOLO model."""
        self.logger.info("Starting model training...")
        results = self.model.train(data=str(self.dataset_yaml_path),
                                    epochs=self.number_of_epochs,
                                    batch=self.batch_size,
                                    imgsz=self.model_image_size,
                                    device=self.device_for_training)
        self.logger.info("Model training completed.")
        return results

    def evaluate(self):
        # Implement the evaluation logic here
        pass
    
    def __str__(self):
        return (f"YOLOmodelTrainer: {self.settings.MODEL_NAME_AND_SIZE}, \n"
                f"dataset_path: {self.dataset_path}, \n"
                f"images_for_training: {self.images_for_training}, \n"
                f"images_for_validation: {self.images_for_validation} \n"
                f"batch_size: {self.batch_size}, \n"
                f"number_of_epochs: {self.number_of_epochs}, \n"
                f"model_image_size: {self.model_image_size}, \n"
                f"device_for_training: {self.device_for_training}")
    
    
    
if __name__ == "__main__":
    model_trainer = YOLOmodelTrainer(logger=logger, settings=settings)
    print(model_trainer)
    model_trainer.train()