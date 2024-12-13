# Window configurations
MAIN_WINDOW_SIZE = "1200x900"
STUDY_WINDOW_SIZE = "1200x900"
CLASS_SELECTION_SIZE = "1200x900"
SETTINGS_WINDOW_SIZE = "1200x900"
ADD_CARDS_WINDOW_SIZE = "1200x900"

# Style configurations
STYLES = {
    "Card.TLabelframe": {
        "background": "#ffffff",
        "borderwidth": 2,
        "relief": "solid"
    },
    "Card.TLabelframe.Label": {  # Frame title
        "font": ("Arial", 14, "bold"),
        "foreground": "#ffffff"  # Changed to white
    },
    "Content.TLabel": {
        "background": "#2c3e50",  # Dark background
        "font": ("Arial", 16),
        "padding": 20,
        "anchor": "center",
        "justify": "center",
        "foreground": "#ffffff"  # White text
    },
    "ShowAnswer.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "width": 30,
        "background": "#3498db",  # Blue background
        "foreground": "#ffffff"  # White text
    },
    "Correct.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "background": "#28a745",
        "foreground": "#ffffff"
    },
    "Wrong.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "background": "#dc3545",
        "foreground": "#ffffff"
    }
}

# Default settings
DEFAULT_FONT_SIZE = 12
DEFAULT_CARDS_PER_SESSION = 20
DEFAULT_SHOW_PROGRESS = True

# Sound settings
ENABLE_SOUNDS = True
SOUND_EFFECTS = {
    'correct': 'assets/sounds/correct.wav',
    'wrong': 'assets/sounds/wrong.wav',
    'flip': 'assets/sounds/flip.wav'
}

# Animation settings
ENABLE_ANIMATIONS = True
ANIMATION_DURATION = 300  # milliseconds
