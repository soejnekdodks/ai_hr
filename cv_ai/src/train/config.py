from pydantic import BaseModel
from pathlib import Path

class TrainingConfig(BaseModel):
    data_path: str
    output_dir: str = "./models/ner_model"
    epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 2e-5
    max_length: int = 128
    val_size: float = 0.2
    model_name: str = "cointegrated/rubert-tiny2"
    random_state: int = 42
    
    def create_output_dir(self):
        """Создание выходной директории"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)