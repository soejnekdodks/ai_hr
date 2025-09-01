class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('russian'))
    
    def clean_text(self, text):
        """Очистка текста"""
        if not text:
            return ""
        
        # Удаление спецсимволов, но сохранение пунктуации
        text = re.sub(r'[^\w\s.,!?;:-]', ' ', str(text))
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize_with_offsets(self, text):
        """Токенизация с позициями"""
        tokens = []
        offsets = []
        
        # Учет сложных конструкций: дат, email, телефонов
        patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # Даты
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{11}\b',  # Телефоны
            r'\w+|[^\w\s]'  # Слова и пунктуация
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                tokens.append(match.group())
                offsets.append((match.start(), match.end()))
        
        return tokens, offsets
    
    def normalize_cv(self, cv_data):
        """Нормализация данных резюме"""
        normalized = {}
        for key, value in cv_data.items():
            if isinstance(value, str):
                normalized[key] = self.clean_text(value)
            elif isinstance(value, list):
                normalized[key] = [self.clean_text(str(item)) for item in value]
            else:
                normalized[key] = value
        return normalized