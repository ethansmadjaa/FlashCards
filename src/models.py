from datetime import datetime, timedelta
from typing import Dict, Any
from .config import DEFAULT_FONT_SIZE, DEFAULT_CARDS_PER_SESSION, DEFAULT_SHOW_PROGRESS
from .utils import save_json, safe_json_load, SETTINGS_FILE, STATS_FILE


class Card:
    DIFFICULTY_COLORS = {
        'easy': '#28a745',    # Green
        'medium': '#ffc107',  # Yellow
        'hard': '#dc3545'     # Red
    }

    def __init__(self, question: str, answer: str, class_name: str):
        self.question = question
        self.answer = answer
        self.class_name = class_name
        self.difficulty = 'medium'  # Default difficulty
        self.level = 0
        self.next_review = datetime.now()

    def set_difficulty(self, difficulty: str) -> None:
        """Set card difficulty (easy, medium, hard)"""
        if difficulty in self.DIFFICULTY_COLORS:
            self.difficulty = difficulty

    def get_difficulty_color(self) -> str:
        """Get the color associated with the card's difficulty"""
        return self.DIFFICULTY_COLORS.get(self.difficulty, self.DIFFICULTY_COLORS['medium'])

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
            "difficulty": self.difficulty,
            "level": self.level,
            "next_review": self.next_review.isoformat()
        }


def save_settings(new_settings: Dict[str, Any]) -> bool:
    return save_json(SETTINGS_FILE, new_settings)


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.settings = {
                "font_size": DEFAULT_FONT_SIZE,
                "cards_per_session": DEFAULT_CARDS_PER_SESSION,
                "show_progress": DEFAULT_SHOW_PROGRESS
            }
            cls._instance.load_settings()
        return cls._instance

    def load_settings(self):
        """Load settings from file"""
        saved_settings = safe_json_load(SETTINGS_FILE, {})
        self.settings.update(saved_settings)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)

    def save_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        self.settings.update(new_settings)
        return save_json(SETTINGS_FILE, self.settings)


class StudyStats:
    def __init__(self):
        self.stats = safe_json_load(STATS_FILE, {})

    def add_session(self, class_name: str, total_cards: int, correct: int, timestamp: str = None) -> None:
        """Add a study session result"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        if class_name not in self.stats:
            self.stats[class_name] = []

        session = {
            "timestamp": timestamp,
            "total_cards": total_cards,
            "correct": correct,
            "accuracy": (correct / total_cards * 100) if total_cards > 0 else 0
        }

        self.stats[class_name].append(session)
        self.save_stats()

    def get_class_stats(self, class_name: str) -> Dict:
        """Get statistics for a specific class"""
        if class_name not in self.stats:
            return {"sessions": 0, "avg_accuracy": 0, "total_cards": 0}

        sessions = self.stats[class_name]
        total_accuracy = sum(s["accuracy"] for s in sessions)
        total_cards = sum(s["total_cards"] for s in sessions)

        return {
            "sessions": len(sessions),
            "avg_accuracy": total_accuracy / len(sessions),
            "total_cards": total_cards,
            "history": sessions
        }

    def get_overall_stats(self) -> Dict:
        """Get overall study statistics"""
        total_sessions = sum(len(sessions) for sessions in self.stats.values())
        total_cards = sum(
            sum(s["total_cards"] for s in sessions)
            for sessions in self.stats.values()
        )
        total_correct = sum(
            sum(s["correct"] for s in sessions)
            for sessions in self.stats.values()
        )

        return {
            "total_sessions": total_sessions,
            "total_cards": total_cards,
            "total_correct": total_correct,
            "overall_accuracy": (total_correct / total_cards * 100) if total_cards > 0 else 0,
            "classes_studied": len(self.stats)
        }

    def save_stats(self) -> bool:
        """Save statistics to file"""
        return save_json(STATS_FILE, self.stats)
