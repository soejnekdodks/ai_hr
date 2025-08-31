import pdfplumber
from docx import Document
import spacy
from sentence_transformers import SentenceTransformer, util
import re
from typing import Dict, Any

# Загрузка моделей (делается один раз при запуске)
nlp = spacy.load("ru_core_news_sm")
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file_path: str) -> str:
    """Извлечение текста из PDF"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Извлечение текста из DOCX"""
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def analyze_resume(file_path: str, vacancy: Dict[str, Any]) -> Dict[str, Any]:
    # Извлечение текста
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    # Обработка текста
    doc = nlp(text)
    
    # Извлечение навыков (упрощенная версия)
    skills = extract_skills(doc)
    experience = extract_experience(text)
    
    # Сравнение с вакансией
    match_score = calculate_match_score(text, vacancy)
    
    return {
        "skills": skills,
        "experience_years": experience,
        "match_score": match_score,
        "missing_skills": list(set(vacancy['required_skills']) - set(skills))
    }

def extract_skills(doc) -> List[str]:
    """Извлечение навыков из текста"""
    skills = []
    skill_keywords = ['python', 'java', 'sql', 'ml', 'ai', 'docker', 'aws']

    for token in doc:
        if token.text.lower() in skill_keywords:
            skills.append(token.text.lower())
    
    return list(set(skills))

def calculate_match_score(resume_text: str, vacancy: Dict[str, Any]) -> float:
    """Расчет совпадения с вакансией"""
    vacancy_text = f"{vacancy['job_title']} {' '.join(vacancy['required_skills'])}"
    
    # Создание эмбеддингов
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    vacancy_embedding = model.encode(vacancy_text, convert_to_tensor=True)
    
    # Расчет косинусной близости
    cosine_score = util.pytorch_cos_sim(resume_embedding, vacancy_embedding).item()
    
    return round(cosine_score, 2)