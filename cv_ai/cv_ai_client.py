# Добавьте в analyzer.py
import requests
import json
from typing import Dict, Any

class CVExternalAnalyzer:
    def __init__(self, service_url: str = "http://cv-ai-service:8001"):
        self.service_url = service_url
    
    def analyze_resume_external(self, file_path: str, vacancy: Dict[str, Any] = None) -> Dict[str, Any]:
        """Анализ резюме через внешний сервис"""
        try:
            # Чтение файла
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                
                # Подготовка данных вакансии, если есть
                data = {}
                if vacancy:
                    data['vacancy'] = json.dumps(vacancy)
                
                # Отправка запроса к внешнему сервису
                response = requests.post(
                    f"{self.service_url}/analyze",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Ошибка внешнего сервиса: {response.status_code}")
                    
        except Exception as e:
            raise Exception(f"Ошибка при обращении к внешнему сервису: {str(e)}")

# Инициализация клиента
external_analyzer = CVExternalAnalyzer()