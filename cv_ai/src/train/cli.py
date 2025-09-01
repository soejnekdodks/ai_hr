import argparse
import logging
from pathlib import Path
from .trainer import NERTrainer
from .data_loader import DataLoader
from .config import TrainingConfig

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('training.log'),
            logging.StreamHandler()
        ]
    )

def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Train NER model for CV parsing')
    
    parser.add_argument('--data-path', type=str, required=True,
                      help='Path to training data JSON')
    parser.add_argument('--output-dir', type=str, default='./models/ner_model',
                      help='Output directory for trained model')
    parser.add_argument('--epochs', type=int, default=3,
                      help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=8,
                      help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                      help='Learning rate')
    parser.add_argument('--max-length', type=int, default=128,
                      help='Maximum sequence length')
    parser.add_argument('--val-size', type=float, default=0.2,
                      help='Validation set size ratio')
    parser.add_argument('--model-name', type=str, default='cointegrated/rubert-tiny2',
                      help='Base model name')
    
    return parser.parse_args()

def main():
    """Основная функция тренировки"""
    setup_logging()
    args = parse_args()
    
    # Создаем конфигурацию
    config = TrainingConfig(
        data_path=args.data_path,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_length=args.max_length,
        val_size=args.val_size,
        model_name=args.model_name
    )
    
    # Загружаем данные
    logging.info(f"Loading data from {config.data_path}")
    data_loader = DataLoader(config.data_path)
    annotated_data = data_loader.load_annotated_data()
    
    # Инициализируем тренер
    trainer = NERTrainer(config)
    
    # Запускаем тренировку
    logging.info("Starting training...")
    try:
        trainer.train(annotated_data)
        logging.info("Training completed successfully!")
    except Exception as e:
        logging.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()