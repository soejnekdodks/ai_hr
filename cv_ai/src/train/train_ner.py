from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
)
from datasets import Dataset
import numpy as np
from typing import Tuple, Dict, Any
from seqeval.metrics import f1_score


def tokenize_and_align_labels(examples: Dict[str, Any]) -> Dict[str, Any]:
    """
    Токенизирует текст и выравнивает метки с subword токенами.

    Args:
        examples: Батч данных из датасета

    Returns:
        Dict: Токенизированные данные с выровненными метками
    """
    # Токенизируем текст
    tokenized_inputs = tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,  # Указываем, что текст уже разбит на слова
        padding="max_length",
        max_length=128,  # Можно увеличить для длинных резюме
        return_tensors=None,  # Возвращаем обычные списки, а не тензоры
    )

    labels = []
    for i, label in enumerate(examples["tags"]):
        # Получаем mapping между токенами и исходными словами
        word_ids = tokenized_inputs.word_ids(batch_index=i)

        previous_word_idx = None
        label_ids = []

        for word_idx in word_ids:
            # Специальные токены ([CLS], [SEP], [PAD]) получают метку -100
            if word_idx is None:
                label_ids.append(-100)
            # Для первого subword-токена слова используем метку слова
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            # Для остальных subword-токенов того же слова ставим -100
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx

        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs


def compute_metrics(p: Tuple[np.ndarray, np.ndarray]) -> Dict[str, float]:
    """
    Вычисляет метрики качества модели durante валидации.

    Args:
        p: Кортеж (predictions, label_ids)

    Returns:
        Dict: Словарь с метриками
    """
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    # Убираем padding и специальные токены (где label = -100)
    true_predictions = [
        [id2label[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [id2label[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    return {
        "f1": f1_score(true_labels, true_predictions),
        "accuracy": (np.array(true_predictions) == np.array(true_labels)).mean(),
    }


def main():
    """Основная функция обучения модели."""
    # 1. Инициализация модели и токенизатора
    model_name = "cointegrated/rubert-tiny2"
    print(f"Загрузка модели {model_name}...")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name, num_labels=len(LABELS), id2label=id2label, label2id=label2id
    )

    # 2. Загрузка и подготовка данных
    print("Загрузка данных...")
    train_texts, train_tags, val_texts, val_tags = load_data()

    # Создаем datasets в формате Hugging Face
    train_dataset = Dataset.from_dict({"tokens": train_texts, "tags": train_tags})
    val_dataset = Dataset.from_dict({"tokens": val_texts, "tags": val_tags})

    # Токенизируем datasets
    print("Токенизация данных...")
    tokenized_train_dataset = train_dataset.map(
        tokenize_and_align_labels,
        batched=True,
        remove_columns=train_dataset.column_names,
    )
    tokenized_val_dataset = val_dataset.map(
        tokenize_and_align_labels, batched=True, remove_columns=val_dataset.column_names
    )

    # 3. Настройка параметров обучения
    training_args = TrainingArguments(
        output_dir="./cv-ner-model",  # Куда сохранять модель
        evaluation_strategy="epoch",  # Оценивать после каждой эпохи
        save_strategy="epoch",  # Сохранять после каждой эпохи
        learning_rate=2e-5,  # Скорость обучения
        per_device_train_batch_size=8,  # Размер батча для обучения
        per_device_eval_batch_size=8,  # Размер батча для оценки
        num_train_epochs=3,  # Количество эпох
        weight_decay=0.01,  # L2 регуляризация
        load_best_model_at_end=True,  # Загружать лучшую модель в конце
        metric_for_best_model="f1",  # По какой метрике выбирать лучшую
        greater_is_better=True,  # Больше F1 = лучше
        logging_dir="./logs",  # Директория для логов
        logging_steps=10,  # Частота логирования
        report_to="none",  # Не отправлять в сторонние сервисы
    )

    # 4. Инициализация DataCollator
    data_collator = DataCollatorForTokenClassification(
        tokenizer=tokenizer, padding=True
    )

    # 5. Создание и запуск Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    print("Начало обучения...")
    train_result = trainer.train()

    # 6. Сохранение результатов
    trainer.save_model()  # Сохраняем лучшую модель
    trainer.log_metrics("train", train_result.metrics)
    trainer.save_metrics("train", train_result.metrics)
    trainer.save_state()

    # 7. Финальная оценка
    print("\nФинальная оценка на validation set:")
    metrics = trainer.evaluate()
    print(metrics)


if __name__ == "__main__":
    main()
