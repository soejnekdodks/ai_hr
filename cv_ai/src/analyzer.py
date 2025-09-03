from .model_init import analyze_cv_pipeline
from .config import config

entities = analyze_cv_pipeline(request.resume_text)

# TODO сделать динамическую генерацию результата в виде словаря списков с ключами по тегам
for tag in config.TAGS:
    skills = [e["word"] for e in entities if e["entity_group"] == "SKILL"]

is_relevant = len(skills) > 5
