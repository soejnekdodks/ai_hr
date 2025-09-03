from transformers import pipeline
from .config import config


analyze_cv_pipeline = pipeline(
    "token-classification",
    model=config.MODEL_PATH,
    aggregation_strategy="simple",
    device=-1,
)
