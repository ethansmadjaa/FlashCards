import json
import os
from typing import Any, Dict, List, Optional

# Constants
FLASHCARD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flashcards.json")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")
STATS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "study_stats.json")


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

    if not os.path.exists(STATS_FILE):
        save_json(STATS_FILE, {})


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


def load_cards_for_class(class_name: Optional[str] = None) -> List[Dict]:
    """Load cards for a specific class or all cards if class_name is None"""
    try:
        print(f"DEBUG: Loading cards from {FLASHCARD_FILE}")  # Debug print
        print(f"DEBUG: Looking for class: {class_name}")  # Debug print
        
        if not os.path.exists(FLASHCARD_FILE):
            print("DEBUG: Flashcard file does not exist")  # Debug print
            return []
            
        cards = safe_json_load(FLASHCARD_FILE, [])
        print(f"DEBUG: Loaded {len(cards)} total cards")  # Debug print
        
        if not cards:
            print("DEBUG: No cards found in file")  # Debug print
            return []
            
        if class_name is None:
            print("DEBUG: Returning all cards")  # Debug print
            return cards
            
        filtered_cards = [card for card in cards if card.get('class_name') == class_name]
        print(f"DEBUG: Found {len(filtered_cards)} cards for class {class_name}")  # Debug print
        if filtered_cards:
            print(f"DEBUG: First filtered card: {filtered_cards[0]}")  # Debug print
        return filtered_cards
        
    except Exception as e:
        print(f"DEBUG: Error loading cards: {e}")  # Debug print
        return []
