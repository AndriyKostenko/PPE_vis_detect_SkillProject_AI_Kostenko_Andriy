from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Application settings for PPE Vision Detector
        - EPOCHS: One full pass over the training data
        - BATCH SIZE: Number of samples processed before the model is updated
        - MODEL IMG SIZE: Dimension to which input images are resized
        - DATASET PATH: Path to the dataset configuration file
    """
    model_config = SettingsConfigDict(env_file=str(_PROJECT_ROOT / ".env"), 
                                      env_file_encoding="utf-8",
                                      case_sensitive=True,
                                      extra="ignore")
    
    # Setting the default params for the application in case user forgets to set them in .env file
    APP_NAME: str = "PPE_Vision_Detector_APP"
    APP_VERSION: str = "0.0.1"
    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    IMAGE_UPLOAD_DIR: str = "uploads"
    INFERENCE_RESULTS_DIR: str = "inference_results"
    
    #YOLO Model settings
    MODEL_NAME_AND_SIZE: str = "yolo11n.pt"  # setting the minimum default model
    TRAINING_DATASET_PATH: str = "dataset/data.yaml"  # dataset config YAML (paths, class names, nc)
    MODEL_IMG_SIZE: int = 640  # training image size (default 640)
    BATCH_SIZE: int = 4 # default smallest batch size
    NUMBER_OF_EPOCHS: int = 10  # let it be only 10 for testing purpose and saving the users GPU/CPU
    CONFIDENCE_THRESHOLD: float = 0.25  # default confidence threshold for inference
    IOU_THRESHOLD: float = 0.45  # default IoU threshold for NMS during inference
    
    @property
    def BASE_DIR(self) -> Path:
        """Get the backend base directory."""
        return _BACKEND_DIR
    
    @property
    def DATASET_PATH(self) -> Path:
        """Get the dataset path."""
        return _BACKEND_DIR / Path(self.TRAINING_DATASET_PATH).parent
    
    @property
    def DATASET_YAML_PATH(self) -> Path:
        """Get the dataset YAML file path."""
        return _BACKEND_DIR / self.TRAINING_DATASET_PATH    
    
    
@lru_cache()
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()


settings = get_settings()