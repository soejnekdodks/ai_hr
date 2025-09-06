from transformers import pipeline
import re

class ContextualNER:
    def __init__(self):
        # Загружаем модель DeepPavlov
        self.pipeline = pipeline(
            "ner",
            model="FacebookAI/xlm-roberta-large-finetuned-conll03-german",
            tokenizer="FacebookAI/xlm-roberta-large-finetuned-conll03-german",
            aggregation_strategy="simple"
        )
        self.ner_to_internal = {
            "PER": "PERSON",
            "LOC": "LOCATION",
            "ORG": "EDUCATION",  # при совпадении с вузом — Education
            "EXPERIENCE": "EXPERIENCE",     # по умолчанию, уточним позже
        }

        self.education_keywords = {
            # Университеты России
            "мгу", "московский государственный университет", "спбгу", "санкт-петербургский государственный университет",
            "мфти", "московский физико-технический институт", "вшэ", "высшая школа экономики",
            "мгту", "мгту баумана", "бауманка", "ранхигс", "финансовый университет", "рггу", "ргту",
            "мгу имени ломоносова", "рудн", "университет дружбы народов", "мифи", "миссис", "гуу",
            "урфу", "тгу", "тюмгу", "нгу", "сгу", "пгу", "дгу", "кфу", "спбпу", "политех", "пгниу",

            # Общие ключи
            "университет", "институт", "академия", "колледж", "техникум", "вузы", "бакалавр",
            "магистр", "аспирант", "phd", "doctoral", "кандидат наук"
        }

        self.skill_keywords = {
            # Языки программирования
            "python", "java", "c", "c++", "c#", "go", "golang", "javascript", "typescript", "php",
            "ruby", "rust", "swift", "kotlin", "scala", "perl", "objective-c", "r", "matlab",

            # Фреймворки и библиотеки
            "django", "flask", "fastapi", "tornado", "aiohttp", "spring", "hibernate",
            "express", "nestjs", "react", "vue", "angular", "svelte", "nextjs", "nuxt",
            "qt", "gtk", "tkinter", "pandas", "numpy", "scipy", "scikit-learn", "tensorflow",
            "pytorch", "keras", "opencv",

            # Базы данных
            "postgres", "postgresql", "mysql", "mariadb", "sqlite", "oracle", "mssql",
            "mongodb", "cassandra", "redis", "dynamodb", "elasticsearch", "neo4j",

            # DevOps / Cloud
            "docker", "kubernetes", "helm", "ansible", "terraform", "jenkins",
            "gitlab-ci", "github actions", "travis", "circleci",
            "aws", "gcp", "azure", "digitalocean", "openstack",

            # Сообщения / шина данных
            "kafka", "rabbitmq", "activemq", "zeromq", "mqtt", "grpc", "rest", "soap",
            "graphql", "websockets",

            # Инструменты
            "git", "svn", "mercurial", "linux", "bash", "powershell", "zsh",
            "make", "cmake", "gradle", "maven", "npm", "yarn", "pnpm",

            # Data science / ML / AI
            "machine learning", "deep learning", "data analysis", "etl", "airflow",
            "hadoop", "spark", "hive", "beam", "mlflow", "huggingface",

            # Другие полезные
            "rest api", "ci/cd", "microservices", "monolith", "distributed systems",
            "highload", "cloud native", "observability", "logging", "monitoring",
            "prometheus", "grafana", "elastic stack"
        }

    def __normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def __map_entity_group(self, ent: dict) -> str:
        text = self.__normalize(ent["word"])
        entity_group = self.ner_to_internal.get(ent["entity_group"], "O")

        if entity_group == "EDUCATION" or any(kw in text for kw in self.education_keywords):
            return "EDUCATION"
        elif entity_group == "EXPERIENCE" or any(kw in text for kw in self.skill_keywords):
            return "EXPERIENCE"
        elif entity_group == "PERSON":
            return "PERSON"
        elif entity_group == "LOCATION":
            return "LOCATION"
        else:
            return "O"

    def extract_entities(self, text: str) -> list[dict]:
        entities = self.pipeline(text)

        results = []
        for ent in entities:
            label = self.__map_entity_group(ent)
            if label == "O":
                continue
            results.append({
                "entity_group": label,
                "score": float(ent["score"]),
                "word": ent["word"],
                "start": ent["start"],
                "end": ent["end"]
            })
        return results