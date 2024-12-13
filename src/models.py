from datetime import datetime, timedelta
from typing import Dict, Any

from .utils import save_json, safe_json_load, SETTINGS_FILE


class Card:
    def __init__(self, question: str, answer: str, class_name: str):
        self.question = question
        self.answer = answer
        self.class_name = class_name
        self.level = 0
        self.next_review = datetime.now()

    def update_level(self, correct: bool) -> None:
        if correct:
            self.level += 1
            days = 2 ** self.level
            self.next_review = datetime.now() + timedelta(days=days)
        else:
            self.level = max(0, self.level - 1)
            self.next_review = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "class_name": self.class_name,
            "level": self.level,
            "next_review": self.next_review.isoformat()
        }


def save_settings(new_settings: Dict[str, Any]) -> bool:
    return save_json(SETTINGS_FILE, new_settings)


class Settings:
    _instance = None

    def __init__(self):
        self.settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.settings = {
            "font_size": 12,
            "cards_per_session": 20,
            "show_progress": True
        }
        self.load_settings()

    def load_settings(self):
        self.settings.update(safe_json_load(SETTINGS_FILE, {}))

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
