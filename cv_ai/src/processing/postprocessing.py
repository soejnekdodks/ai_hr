class ResultPostprocessor:
    def __init__(self):
        self.entity_rules = {
            'PERSON': self._validate_person,
            'DATE': self._validate_date,
            'EMAIL': self._validate_email,
            'PHONE': self._validate_phone
        }
    
    def structure_entities(self, entities, original_text):
        """Структурирование извлеченных сущностей"""
        structured = {
            'personal_info': {
                'name': None,
                'contacts': [],
                'location': None
            },
            'education': [],
            'experience': [],
            'skills': {
                'technical': [],
                'soft': [],
                'languages': []
            },
            'metadata': {
                'processing_date': datetime.now().isoformat(),
                'confidence_scores': {}
            }
        }
        
        for entity in entities:
            self._assign_entity(structured, entity)
        
        return structured
    
    def _assign_entity(self, structured, entity):
        """Распределение сущностей по категориям"""
        entity_type = entity['type']
        text = entity['text']
        
        if entity_type == 'PERSON':
            structured['personal_info']['name'] = text
        elif entity_type == 'LOCATION':
            structured['personal_info']['location'] = text
        elif entity_type == 'EMAIL':
            structured['personal_info']['contacts'].append(
                {'type': 'email', 'value': text}
            )
        # ... другие правила
