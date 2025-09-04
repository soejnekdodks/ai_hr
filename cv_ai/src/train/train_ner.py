import logging
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification,
    TrainingArguments, 
    Trainer,
    DataCollatorForTokenClassification
)
from sklearn.model_selection import train_test_split
from datasets import Dataset
import numpy as np
from .config import TrainingConfig

# Метки для NER
LABELS = [
    "O", "B-PERSON", "I-PERSON", "B-LOCATION", "I-LOCATION",
    "B-POSITION", "I-POSITION", "B-SKILL", "I-SKILL", "B-COMPANY", "I-COMPANY",
    "B-DATE", "I-DATE", "B-EMAIL", "I-EMAIL", "B-PHONE", "I-PHONE"
]

class NERTrainer:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        
        # Создаем mapping меток
        self.id2label = {i: label for i, label in enumerate(LABELS)}
        self.label2id = {label: i for i, label in enumerate(LABELS)}
        
        self.model = AutoModelForTokenClassification.from_pretrained(
            config.model_name,
            num_labels=len(LABELS),
            id2label=self.id2label,
            label2id=self.label2id
        )
        
        # Создаем выходную директорию
        self.config.create_output_dir()
    
    def prepare_datasets(self, annotated_data):
        """Подготовка datasets для обучения"""
        texts = [item['text'] for item in annotated_data]
        tags = [self._convert_annotations_to_tags(item) for item in annotated_data]
        
        # Разделяем на train/validation
        train_texts, val_texts, train_tags, val_tags = train_test_split(
            texts, tags, 
            test_size=self.config.val_size, 
            random_state=self.config.random_state
        )
        
        train_dataset = Dataset.from_dict({
            "tokens": [[word for word in text.split()] for text in train_texts],
            "ner_tags": train_tags
        })
        
        val_dataset = Dataset.from_dict({
            "tokens": [[word for word in text.split()] for text in val_texts],
            "ner_tags": val_tags
        })
        
        return train_dataset, val_dataset
    
    def _convert_annotations_to_tags(self, item):
        """Конвертация аннотаций в метки токенов"""
        text = item['text']
        annotations = item['annotations']
        tokens = text.split()
        tags = ['O'] * len(tokens)
        
        for ann in annotations:
            entity_text = text[ann['start']:ann['end']]
            entity_tokens = entity_text.split()
            
            # Находим позицию entity в tokens
            for i in range(len(tokens) - len(entity_tokens) + 1):
                if tokens[i:i+len(entity_tokens)] == entity_tokens:
                    tags[i] = f"B-{ann['label']}"
                    for j in range(1, len(entity_tokens)):
                        tags[i+j] = f"I-{ann['label']}"
                    break
        
        return [self.label2id[tag] for tag in tags]
    
    def tokenize_and_align_labels(self, examples):
        """Выравнивание меток с subword токенами"""
        tokenized_inputs = self.tokenizer(
            examples["tokens"],
            truncation=True,
            is_split_into_words=True,
            padding="max_length",
            max_length=self.config.max_length,
        )
        
        labels = []
        for i, label in enumerate(examples["ner_tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []
            
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)
                elif word_idx != previous_word_idx:
                    label_ids.append(label[word_idx])
                else:
                    label_ids.append(-100)
                previous_word_idx = word_idx
            
            labels.append(label_ids)
        
        tokenized_inputs["labels"] = labels
        return tokenized_inputs
    
    def compute_metrics(self, eval_pred):
        """Вычисление метрик"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=2)
        
        # Убираем padding токены
        true_predictions = [
            [self.id2label[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [self.id2label[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        
        # Вычисляем метрики
        precision = self._calculate_precision(true_predictions, true_labels)
        recall = self._calculate_recall(true_predictions, true_labels)
        f1 = self._calculate_f1(precision, recall)
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    
    def train(self, annotated_data):
        """Процесс обучения"""
        # Подготовка данных
        train_dataset, val_dataset = self.prepare_datasets(annotated_data)
        
        # Токенизация
        tokenized_train = train_dataset.map(
            self.tokenize_and_align_labels,
            batched=True,
            remove_columns=train_dataset.column_names
        )
        
        tokenized_val = val_dataset.map(
            self.tokenize_and_align_labels,
            batched=True,
            remove_columns=val_dataset.column_names
        )
        
        # Настройка training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            learning_rate=self.config.learning_rate,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            logging_dir=f"{self.config.output_dir}/logs",
            logging_steps=10,
            report_to="none"
        )
        
        # Data collator
        data_collator = DataCollatorForTokenClassification(
            tokenizer=self.tokenizer
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_val,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics
        )
        
        # Запуск обучения
        logging.info("Starting training process...")
        trainer.train()
        
        # Сохранение модели
        trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        logging.info(f"Model saved to {self.config.output_dir}")