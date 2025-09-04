import json

import numpy as np
from datasets import Dataset
from seqeval.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
)


class IncrementalNERTrainer:
    def __init__(self, config, new_labels=None):
        """
        config:
            model_name - путь или huggingface id
            labels - старые лейблы
            output_dir - куда сохранять
        new_labels:
            список новых лейблов (например ["B-EXPERIENCE", "I-EXPERIENCE"])
        """
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config["model_name"])

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Загружаем модель
        base_model = AutoModelForTokenClassification.from_pretrained(
            config["model_name"]
        )

        old_id2label = base_model.config.id2label
        old_label2id = base_model.config.label2id

        # Обновляем список лейблов
        all_labels = config["labels"].copy()
        if new_labels:
            for lbl in new_labels:
                if lbl not in all_labels:
                    all_labels.append(lbl)

        self.labels = all_labels
        self.id2label = {i: l for i, l in enumerate(self.labels)}
        self.label2id = {l: i for i, l in enumerate(self.labels)}

        # Если количество лейблов изменилось — переинициализируем classification head
        if len(self.labels) != base_model.num_labels:
            print(
                f"⚠️ Меняем число классов: {base_model.num_labels} → {len(self.labels)}"
            )

            self.model = AutoModelForTokenClassification.from_pretrained(
                config["model_name"],
                num_labels=len(self.labels),
                id2label=self.id2label,
                label2id=self.label2id,
                ignore_mismatched_sizes=True,  # ⚠️ важно!
            )
        else:
            self.model = base_model

    def load_dataset(self, dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def prepare_datasets(self, annotated_data):
        """Заготовка: токенизация и BIO → ID"""
        all_tokens = []
        all_labels = []

        for item in annotated_data:
            text = item["text"]
            annotations = item["annotations"]

            # char-level метки
            char_labels = ["O"] * len(text)
            for ann in annotations:
                start, end = ann["start"], ann["end"]
                label = ann["label"]
                if start < end <= len(text):
                    char_labels[start] = f"B-{label}"
                    for i in range(start + 1, end):
                        char_labels[i] = f"I-{label}"

            # токенизация
            tokenized = self.tokenizer(
                text,
                truncation=True,
                max_length=512,
                return_offsets_mapping=True,
                add_special_tokens=False,
            )

            token_labels = []
            for start, end in tokenized["offset_mapping"]:
                if start == end:
                    token_labels.append("O")
                else:
                    token_labels.append(char_labels[start])

            label_ids = [self.label2id.get(l, self.label2id["O"]) for l in token_labels]

            all_tokens.append(tokenized["input_ids"])
            all_labels.append(label_ids)

        train_tokens, val_tokens, train_labels, val_labels = train_test_split(
            all_tokens, all_labels, test_size=0.2, random_state=42
        )
        return train_tokens, val_tokens, train_labels, val_labels

    def tokenize_and_align_labels(self, examples):
        texts = [
            self.tokenizer.decode(t, skip_special_tokens=True)
            for t in examples["tokens"]
        ]
        tokenized_inputs = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt",
            is_split_into_words=False,
        )

        labels = []
        for i, label_seq in enumerate(examples["ner_tags"]):
            seq_len = len(tokenized_inputs["input_ids"][i])
            if len(label_seq) > seq_len:
                aligned = label_seq[:seq_len]
            else:
                aligned = label_seq + [-100] * (seq_len - len(label_seq))
            labels.append(aligned)

        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    def compute_metrics(self, eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=2)

        true_preds, true_labels = [], []
        for pred, lab in zip(predictions, labels):
            pred_seq, lab_seq = [], []
            for p, l in zip(pred, lab):
                if l != -100:
                    pred_seq.append(self.id2label[p])
                    lab_seq.append(self.id2label[l])
            true_preds.append(pred_seq)
            true_labels.append(lab_seq)

        return {
            "precision": precision_score(true_labels, true_preds),
            "recall": recall_score(true_labels, true_preds),
            "f1": f1_score(true_labels, true_preds),
        }

    def train(self, train_data, val_data):
        train_dataset = Dataset.from_dict(
            {"tokens": train_data[0], "ner_tags": train_data[1]}
        )
        val_dataset = Dataset.from_dict(
            {"tokens": val_data[0], "ner_tags": val_data[1]}
        )

        tokenized_train = train_dataset.map(
            self.tokenize_and_align_labels, batched=True
        )
        tokenized_val = val_dataset.map(self.tokenize_and_align_labels, batched=True)

        args = TrainingArguments(
            output_dir=self.config["output_dir"],
            num_train_epochs=self.config["epochs"],
            per_device_train_batch_size=self.config["batch_size"],
            per_device_eval_batch_size=self.config["batch_size"],
            learning_rate=self.config["learning_rate"],
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            logging_steps=50,
        )

        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_val,
            tokenizer=self.tokenizer,
            data_collator=DataCollatorForTokenClassification(tokenizer=self.tokenizer),
            compute_metrics=self.compute_metrics,
        )

        trainer.train()
        trainer.save_model(self.config["output_dir"])
        return trainer


config = {
    "model_name": "FacebookAI/xlm-roberta-large-finetuned-conll03-german",  # можно путь к своей модели
    "labels": [
        "O",
        "B-LOCATION",
        "I-LOCATION",
        "B-EDUCATION",
        "I-EDUCATION",
        "B-PERSON",
        "I-PERSON",
    ],
    "output_dir": "/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/ner_model",
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 3e-5,
}

trainer = IncrementalNERTrainer(config, new_labels=["B-EXPERIENCE", "I-EXPERIENCE"])

annotated_data = trainer.load_dataset(
    "/Users/brmstr/Repos/ai_hr/ai_hr/cv_ai/src/dataset/dataset_30000.json"
)
train_tokens, val_tokens, train_labels, val_labels = trainer.prepare_datasets(
    annotated_data
)

trainer.train([train_tokens, train_labels], [val_tokens, val_labels])
