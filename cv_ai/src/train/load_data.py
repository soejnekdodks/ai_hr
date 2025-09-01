import json
import logging
from typing import List, Dict, Any

class DataLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path
    
    def load_annotated_data(self) -> List[Dict[str, Any]]:
        """Загрузка размеченных данных"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logging.info(f"Loaded {len(data)} annotated examples")
            return data
            
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise
    
    def stream_large_json(self, batch_size: int = 1000):
        """Потоковая загрузка больших JSON файлов"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            batch = []
            for line in f:
                try:
                    item = json.loads(line.strip().rstrip(','))
                    batch.append(item)
                    
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []
                        
                except json.JSONDecodeError as e:
                    logging.warning(f"Skipping invalid JSON line: {e}")
                    continue
            
            if batch:
                yield batch