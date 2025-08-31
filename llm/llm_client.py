import requests
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.base_url = os.getenv("LLM_SERVICE_URL", "http://llm-service:11434")
    
    def chat(self, prompt: str, model: str = "llama3") -> str:
        """Отправляет запрос к внешнему LLM сервису"""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise Exception(f"Ошибка при обращении к LLM сервису: {str(e)}")

llm_client = LLMClient()