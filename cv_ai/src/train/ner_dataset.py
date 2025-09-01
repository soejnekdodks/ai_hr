from torch.utils.data import Dataset
import torch

class NERDataset(Dataset):
    def __init__(self, annotated_data, tokenizer, max_length=128):
        self.data = annotated_data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        text = item['text']
        annotations = item['annotations']
        
        # Токенизация
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt',
            return_offsets_mapping=True
        )
        
        # Создаем метки
        labels = self._create_labels(encoding, annotations)
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': labels,
            'text': text
        }
    
    def _create_labels(self, encoding, annotations):
        """Создание меток для NER"""
        labels = torch.full((self.max_length,), -100, dtype=torch.long)
        offset_mapping = encoding['offset_mapping'][0]
        
        for ann in annotations:
            start_char, end_char = ann['start'], ann['end']
            label = ann['label']
            
            # Находим токены, соответствующие сущности
            for i, (start, end) in enumerate(offset_mapping):
                if start >= self.max_length:
                    break
                    
                # Проверяем пересечение токена с сущностью
                if not (end <= start_char or start >= end_char):
                    # Определяем тип метки (B- или I-)
                    if start >= start_char and labels[i] == -100:
                        prefix = "B-" if labels[i] == -100 else "I-"
                        labels[i] = self.label2id.get(f"{prefix}{label}", -100)
        
        return labels