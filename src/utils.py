import json
import os
from typing import Any, Dict, List

# Constants
FLASHCARD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flashcards.json")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")


def safe_json_load(file_path: str, default_value: Any) -> Any:
    """Safely load JSON file with error handling"""
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Error loading {file_path}: {str(e)}")
        return default_value


def save_json(file_path: str, data: Any) -> bool:
    """Save data to JSON file with error handling"""
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving to {file_path}: {str(e)}")
        return False


def initialize_files() -> None:
    """Initialize necessary files if they don't exist"""
    if not os.path.exists(FLASHCARD_FILE):
        save_json(FLASHCARD_FILE, [])

    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "font_size": 12,
            "cards_per_session": 20,
            "show_progress": True
        }
        save_json(SETTINGS_FILE, default_settings)


def get_available_classes() -> set:
    """Get all available class names from flashcards"""
    classes = set()
    try:
        flashcards = safe_json_load(FLASHCARD_FILE, [])
        for card in flashcards:
            if "class_name" in card:
                classes.add(card["class_name"])
    except Exception as e:
        print(f"Error reading classes: {str(e)}")
    return classes


def load_cards_for_class(class_name: str = None) -> List[Dict]:
    """Load cards for a specific class or all cards if class_name is None"""
    all_cards = safe_json_load(FLASHCARD_FILE, [])
    if class_name is None:
        return all_cards
    return [card for card in all_cards if card['class_name'].lower() == class_name.lower()]
