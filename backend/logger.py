import logging
from typing import Optional
from pathlib import Path


class Logger:
    """A customizable logger class for logging messages to console and/or file."""
    def __init__(self, 
                 name: str, 
                 log_level: str = "INFO", 
                 log_dir: Optional[str] = None,
                 log_to_file: bool = True,
                 log_to_console: bool = True) -> None:
        self.name = name
        self.log_level = log_level
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).parent / "logs"
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.log_level.upper()))
        self._setup_handlers()
        
    def _setup_handlers(self) -> None:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        if self.log_to_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_dir / f"{self.name}.log")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
    def debug(self, message: str) -> None:
        self.logger.debug(message)
        
    def info(self, message: str) -> None:
        self.logger.info(message)
        
    def warning(self, message: str) -> None:
        self.logger.warning(message)
        
    def error(self, message: str) -> None:
        self.logger.error(message)
        
    def critical(self, message: str) -> None:
        self.logger.critical(message)
    
    
logger = Logger(name="PPE Vision Detection Logger", log_to_console=True, log_to_file=True)  
    
    
if __name__ == "__main__":
    logger = Logger(name="test_logger", log_to_console=True, log_to_file=True)
    logger.info("This is an info message.")
    logger.error("This is an error message.")
