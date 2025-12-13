from pathlib import Path
from typing import Optional
import shutil

from ultralytics import YOLO
import torch
import shutil

from settings import Settings, settings
from logger import Logger, logger


class YOLOmodelTrainer:
    def __init__(self, logger: Logger, settings: Settings):
        self.logger = logger
        self.settings = settings
        
        self.dataset_yaml_path = self.settings.DATASET_YAML_PATH
        self.dataset_path = self.settings.DATASET_PATH
        
        if not self.dataset_yaml_path.exists() or not self.dataset_path.exists():
            self.logger.error(f"Dataset YAML or Dataset folder not found: {self.dataset_yaml_path} or {self.dataset_path}")
            raise ValueError(f"Training dataset YAML or folder not found: {self.dataset_yaml_path} or {self.dataset_path}")

        
        # Define output directory in your project
        self.output_dir = self.settings.BASE_DIR / "runs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Where to copy the final best model for easy access
        self.trained_models_dir = self.settings.BASE_DIR / "trained_models"
        self.trained_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model setup
        self.model = YOLO(self.settings.MODEL_NAME_AND_SIZE)
        self.images_for_training = len(list(self.dataset_path.glob('train/images/*.jpg')))
        self.images_for_validation = len(list(self.dataset_path.glob('valid/images/*.jpg')))
        self.model_image_size = self.settings.MODEL_IMG_SIZE
        
        # Detecting device and VRAM FIRST (other methods depend on these)
        self.device_for_training = self._detect_device_for_training()
        self.vram_gb = self._detect_vram_gb()
        
        # Now detecting batch size and epochs (these use vram_gb)
        self.batch_size = self._detect_batch_size_based_on_vram(requested_batch_size=self.settings.BATCH_SIZE)
        self.number_of_epochs = self._detect_number_of_epochs(requested_epochs=self.settings.NUMBER_OF_EPOCHS)
        
        self.best_model_path = None
        self.last_trained_model = None
        
    def _detect_vram_gb(self) -> float:
        """Detect available VRAM in GB."""
        if torch.cuda.is_available():
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = round(vram_bytes / (1024 ** 3))  # Convert bytes to GB
            self.logger.info(f"Detected VRAM: {vram_gb} GB")
            return vram_gb
        else:
            self.logger.info("CUDA not available. VRAM detection skipped.")
            return 0.0 # No GPU available
        
    def _detect_batch_size_based_on_vram(self, requested_batch_size: Optional[int] = None) -> int:
        """Detect batch size based on available VRAM."""
        if self.vram_gb == 0:
            self.logger.warning("No GPU detected. Using CPU with batch size of 4.")
            return 4  # Default batch size for CPU training
        
        if self.vram_gb >= 22:
            max_safe_batch_size = 32
        elif self.vram_gb >= 16:
            max_safe_batch_size = 24
        elif self.vram_gb >= 12:
            max_safe_batch_size = 16
        elif self.vram_gb >= 8:
            max_safe_batch_size = 8
        elif self.vram_gb >= 4:
            max_safe_batch_size = 4
        else:
            self.logger.warning("Low VRAM detected. Using batch size of 2.")
            max_safe_batch_size = 2
        
        self.logger.info(f"Recommended max safe batch size based on VRAM: {max_safe_batch_size}")
        
        # Allow user override, but cap at max_safe_batch_size
        if requested_batch_size is not None and requested_batch_size > 0:
            if requested_batch_size > max_safe_batch_size:
                self.logger.warning(
                    f"Requested batch size {requested_batch_size} exceeds safe limit. "
                    f"Capping to {max_safe_batch_size}."
                )
                return max_safe_batch_size
            self.logger.info(f"Using user-requested batch size: {requested_batch_size}")
            return requested_batch_size
        
        self.logger.info(f"Final batch size set to: {max_safe_batch_size}")
        return max_safe_batch_size
        
    def _detect_device_for_training(self) -> str:
        """Detect if CUDA is available for training."""
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.logger.info(f"Using device for training: {device}")
        return device
    
    def _detect_number_of_epochs(self, requested_epochs: Optional[int] = None) -> int:
        """
        Detect number of epochs based on dataset size.
        User can override with any value via requested_epochs.
        
        Guidelines:
        - Very Small (<1,000 images): 10-50 epochs (high overfitting risk)
        - Small/Custom (1,000-10,000 images): 50-100 epochs
        - Medium (10,000-100,000 images): 100-200 epochs
        - Large (100,000+ images): 300-500+ epochs
        """
        if self.images_for_training == 0:
            self.logger.warning("No training images found!!!")
            return 0
        
        # Calculate recommended epochs based on dataset size
        if self.images_for_training < 1000:
            recommended = 50
            self.logger.info(
                f"Very small dataset ({self.images_for_training} images). "
                f"Recommended epochs: {recommended}. High overfitting risk - using early stopping."
            )
        elif self.images_for_training < 10000:
            recommended = 100
            self.logger.info(
                f"Small/Custom dataset ({self.images_for_training} images). "
                f"Recommended epochs: {recommended}."
            )
        elif self.images_for_training < 100000:
            recommended = 150
            self.logger.info(
                f"Medium dataset ({self.images_for_training} images). "
                f"Recommended epochs: {recommended}."
            )
        else:
            # >= 100,000 images
            recommended = 300
            self.logger.info(
                f"Large dataset ({self.images_for_training} images). "
                f"Recommended epochs: {recommended}."
            )
        
        # Allow user to override with any value (lower OR higher)
        if requested_epochs is not None and requested_epochs > 0:
            if requested_epochs != recommended:
                self.logger.info(
                    f"User override: {requested_epochs} epochs "
                    f"(recommended was {recommended})"
                )
            return requested_epochs
        
        self.logger.info(f"Final number of epochs set to: {recommended}")
        return recommended
        
    def train(self):
        """Train the YOLO model."""
        if self.images_for_training == 0 or self.images_for_validation == 0:
            self.logger.error("No training or validation images found in the dataset.")
            raise ValueError("Dataset is empty. Please check the dataset path and contents.")
        
        if self.number_of_epochs <= 0:
            self.logger.error("Number of epochs must be greater than zero.")
            raise ValueError("Invalid number of epochs specified.")
        
        self.logger.info("Starting model training...")
        results = self.model.train(data=str(self.dataset_yaml_path),
                                    epochs=self.number_of_epochs,
                                    batch=self.batch_size,
                                    imgsz=self.model_image_size,
                                    device=self.device_for_training,
                                    project=str(self.output_dir),
                                    name="ppe_detection_model", # Run name (creates ppe_detector, ppe_detector2, etc.)
                                    exist_ok=False)  # Create new folder each run
        self.logger.info(f"Model training completed. Results saved to: {results.save_dir}")
        
        # Get paths from training results
        save_dir = Path(results.save_dir)
        best_weights = save_dir / "weights" / "best.pt"
        
        self.logger.info(f"Training completed. Results saved to: {save_dir}")
        
        if best_weights.exists():
            self.last_trained_model = YOLO(best_weights)
            self.logger.info(f"Best model weights found at: {best_weights}")
            
            # Copy best model to trained_models_dir for easy access
            final_model_path = self.trained_models_dir / "best_ppe_model.pt"
            shutil.copy(best_weights, final_model_path)
            self.best_model_path = final_model_path
            self.logger.info(f"Best model copied to: {final_model_path}")
        else: 
            self.logger.warning("Best model weights not found after training.")
        return results

    def evaluate(self):
        """Evaluate the trained model on the validation dataset."""
        if not self.last_trained_model:
            self.logger.error("No trained model available for evaluation.")
            raise ValueError("Model has not been trained yet.")
        
        self.logger.info("Starting model evaluation...")
        metrics = self.last_trained_model.val()
        self.logger.info("Model evaluation completed.")
        return metrics
    
    def __str__(self):
        return (f"YOLOmodelTrainer: {self.settings.MODEL_NAME_AND_SIZE}, \n"
                f"dataset_path: {self.dataset_path}, \n"
                f"images_for_training: {self.images_for_training}, \n"
                f"images_for_validation: {self.images_for_validation} \n"
                f"batch_size: {self.batch_size}, \n"
                f"number_of_epochs: {self.number_of_epochs}, \n"
                f"model_image_size: {self.model_image_size}, \n"
                f"device_for_training: {self.device_for_training}, \n"
                f"vram_gb: {self.vram_gb} GB \n"
                f"classes: {self.last_trained_model.names if self.last_trained_model else 'N/A'}"
               )
    
    
    
if __name__ == "__main__":
    model_trainer = YOLOmodelTrainer(logger=logger, settings=settings)
    #print(model_trainer)

    # model_trainer.train()
    
    # Load previously trained model
    # best_model_path = model_trainer.trained_models_dir / "best_ppe_model.pt"
    # if best_model_path.exists():
    #     model_trainer.last_trained_model = YOLO(best_model_path)
    #     model_trainer.best_model_path = best_model_path
    #     logger.info(f"Loaded existing model from: {best_model_path}")
    #     print(model_trainer.evaluate())
    # else:
    #     logger.error(f"No trained model found at {best_model_path}. Run training first.")
