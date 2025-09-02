import json
from typing import Dict, Any

# {
#   "text": "Калужская область Мосальский район г Мосальск Подсобный рабочий ООО Омега сборщик обуви",
#   "annotations": [
#     {"start": 0, "end": 15, "label": "LOCATION"},
#     {"start": 16, "end": 32, "label": "LOCATION"},
#     {"start": 33, "end": 44, "label": "LOCATION"},
#     {"start": 45, "end": 61, "label": "POSITION"},
#     {"start": 62, "end": 70, "label": "COMPANY"},
#     {"start": 71, "end": 84, "label": "POSITION"}
#   ]
# }

def extract_ner_annotations(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Извлекает текст и аннотации из данных резюме"""
    
    text_parts = []
    annotations = []
    current_pos = 0
    
    # Извлекаем сущности из разных полей
    fields_to_extract = [
        ('localityName', 'LOCATION'),
        ('positionName', 'POSITION'),
        ('companyName', 'COMPANY'),
        ('jobTitle', 'POSITION'),
        ('instituteName', 'EDUCATION'),
        ('skills', 'SKILL'),
        ('languageKnowledge', 'LANGUAGE')
    ]
    
    for field, label in fields_to_extract:
        if field in cv_data and cv_data[field]:
            value = cv_data[field]
            
            if isinstance(value, str) and value.strip():
                # Добавляем текст
                text_parts.append(value)
                
                # Добавляем аннотацию
                start = current_pos
                end = current_pos + len(value)
                annotations.append({
                    "start": start,
                    "end": end, 
                    "label": label
                })
                
                current_pos = end + 1  # +1 для пробела
    
    # Собираем полный текст
    full_text = " ".join(text_parts)
    
    return {
        "text": full_text,
        "annotations": annotations
    }

def create_ner_dataset(cv_json_path: str, output_path: str) -> list[dict]:
    """Создает датасет для обучения NER из JSON резюме"""
    
    with open(cv_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    annotated_data = []
    
    for cv in data['cvs']:
        try:
            annotated = extract_ner_annotations(cv)
            if annotated['annotations']:  # Только если есть аннотации
                annotated_data.append(annotated)
        except Exception as e:
            print(f"Error processing CV: {e}")
            continue
    
    # Сохраняем датасет
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(annotated_data, f, ensure_ascii=False, indent=2)
    
    print(f"Created dataset with {len(annotated_data)} examples")
    return annotated_data

# Использование
create_ner_dataset('cv_data.json', 'ner_dataset.json')