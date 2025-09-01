class CVParserPipeline:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.initialize_components()
    
    def initialize_components(self):
        """Инициализация всех компонентов"""
        self.data_loader = DataStreamer(
            self.config['data_path'],
            self.config['batch_size']
        )
        self.preprocessor = TextPreprocessor()
        self.ner_model = NERModel(self.config['model_path'])
        self.postprocessor = ResultPostprocessor()
        self.cache = RedisCache() if self.config['use_cache'] else SimpleCache()
    
    async def process_stream(self):
        """Асинхронная обработка потока данных"""
        async for batch in self.data_loader.async_stream():
            processed_batch = await self.process_batch(batch)
            yield processed_batch
    
    async def process_batch(self, batch):
        """Обработка батча данных"""
        results = []
        
        for cv_data in batch:
            # Предобработка
            normalized = self.preprocessor.normalize_cv(cv_data)
            text = self.extract_text_for_ner(normalized)
            
            # Кеширование
            cache_key = self.generate_cache_key(text)
            if cached := self.cache.get(cache_key):
                results.append(cached)
                continue
            
            # NER обработка
            entities = await self.ner_model.predict_async(text)
            structured = self.postprocessor.structure_entities(entities, text)
            
            # Сохранение в кеш
            self.cache.set(cache_key, structured)
            results.append(structured)
        
        return results
    
    def run(self):
        """Запуск пайплайна"""
        for batch in self.data_loader.stream_jsonl():
            results = self.process_batch_sync(batch)
            self.save_results(results)
            self.monitor.progress_update(len(results))