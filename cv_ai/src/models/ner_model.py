class NERModel:
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.initialize_model()
    
    def initialize_model(self):
        """Инициализация новой модели"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            "cointegrated/rubert-tiny2",
            add_prefix_space=True
        )
        
        self.model = AutoModelForTokenClassification.from_pretrained(
            "cointegrated/rubert-tiny2",
            num_labels=len(LABEL_MAPPING),
            id2label=ID_TO_LABEL,
            label2id=LABEL_TO_ID
        ).to(self.device)
    
    def predict_batch(self, texts_batch):
        """Предсказание для батча текстов"""
        tokenized = self.tokenizer(
            texts_batch,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
            is_split_into_words=False
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**tokenized)
        
        return self.process_predictions(outputs, tokenized, texts_batch)
    
    def process_predictions(self, outputs, tokenized, original_texts):
        """Обработка предсказаний"""
        predictions = torch.argmax(outputs.logits, dim=-1)
        results = []
        
        for i, (text, preds) in enumerate(zip(original_texts, predictions)):
            word_ids = tokenized.word_ids(batch_index=i)
            entities = self.extract_entities(text, preds, word_ids)
            results.append(entities)
        
        return results