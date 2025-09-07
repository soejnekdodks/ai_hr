from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np
from typing import List, Dict, Tuple

from ner import ResumeParser
from config import config


def _pairwise_match(resume_items: List[str], vacancy_items: List[str], embedder) -> Tuple[List[Tuple[str, str, float]], np.ndarray]:
    """Сопоставляет элементы по эмбеддингам, возвращает лучшие пары и матрицу сходства."""
    if not resume_items or not vacancy_items:
        return [], np.zeros((len(vacancy_items), len(resume_items)))

    emb_r = embedder.encode(resume_items, convert_to_tensor=True, normalize_embeddings=True)
    emb_v = embedder.encode(vacancy_items, convert_to_tensor=True, normalize_embeddings=True)

    sim = util.cos_sim(emb_v, emb_r).cpu().numpy()  # [V, R]
    pairs = []
    used_r = set()
    for i, v_item in enumerate(vacancy_items):
        # Находим лучшую пару для каждого vacancy-элемента
        j = int(np.argmax(sim[i])) if sim.shape[1] > 0 else -1
        if sim.shape[1] == 0:
            continue
        score = float(sim[i, j])
        if score >= config.MATCH_THRESHOLD and j not in used_r:
            pairs.append((v_item, resume_items[j], score))
            used_r.add(j)
    return pairs, sim


class ResumeVacancyMatcher:
    def __init__(self):
        self.parser = ResumeParser()
        self.embedder = SentenceTransformer(config.SEMANTIC_MODEL_NAME)

    def match(self, resume_text: str, vacancy_text: str) -> dict:
        # Извлечение сущностей в структуре JSON
        resume_data = self.parser.extract_entities(resume_text, mode="resume")
        vacancy_data = self.parser.extract_entities(vacancy_text, mode="vacancy")

        # По каким лейблам сравниваем (обычно SKILL)
        labels = config.METRIC_LABELS

        matched = {}
        metrics = {}

        # Считаем метрики по каждому лейблу отдельно
        for label in labels:
            r_items = resume_data.get(label, [])
            v_items = vacancy_data.get(label, [])

            pairs, sim = _pairwise_match(r_items, v_items, self.embedder)

            # Для метрик: для каждого vacancy-элемента — 1, если есть пара >= threshold
            y_true = np.ones(len(v_items), dtype=int)
            y_pred = np.zeros(len(v_items), dtype=int)
            v_to_r = {v: (r, s) for (v, r, s) in pairs}
            for idx, v in enumerate(v_items):
                if v in v_to_r:
                    y_pred[idx] = 1

            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)

            matched[label] = {
                "pairs": [
                    {"vacancy": v, "resume": r, "score": round(float(s), 3)}
                    for (v, r, s) in pairs
                ],
                "threshold": config.MATCH_THRESHOLD,
            }
            metrics[label] = {
                "precision": round(float(precision), 3),
                "recall": round(float(recall), 3),
                "f1": round(float(f1), 3),
                "n_vacancy": len(v_items),
                "n_resume": len(r_items),
            }

        # Итоговые агрегированные метрики (по всем лейблам)
        all_true = []
        all_pred = []
        for label in labels:
            v_items = vacancy_data.get(label, [])
            pairs = matched[label]["pairs"]
            v_positive = {p["vacancy"] for p in pairs}
            all_true.extend([1] * len(v_items))
            all_pred.extend([1 if v in v_positive else 0 for v in v_items])

        if all_true:
            agg_precision = precision_score(all_true, all_pred, zero_division=0)
            agg_recall = recall_score(all_true, all_pred, zero_division=0)
            agg_f1 = f1_score(all_true, all_pred, zero_division=0)
        else:
            agg_precision = agg_recall = agg_f1 = 0.0

        return {
            "precision": round(float(agg_precision), 3),
            "recall": round(float(agg_recall), 3),
            "f1": round(float(agg_f1), 3),
            "metrics_by_label": metrics,
            "matched": matched,
            "resume": resume_data,
            "vacancy": vacancy_data,
        }
