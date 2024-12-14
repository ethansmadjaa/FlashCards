# Window configurations
MAIN_WINDOW_SIZE = "1200x900"
STUDY_WINDOW_SIZE = "1200x900"
CLASS_SELECTION_SIZE = "1200x900"
SETTINGS_WINDOW_SIZE = "1200x900"
ADD_CARDS_WINDOW_SIZE = "1200x900"

# Style configurations
STYLES = {
    "Card.TLabelframe": {
        "background": "#ffffff",  # White background
        "borderwidth": 2,
        "relief": "solid"
    },
    "Card.TLabelframe.Label": {  # Frame title
        "font": ("Arial", 14, "bold"),
        "foreground": "#2c3e50",  # Dark text
        "background": "#ffffff"   # White background
    },
    "Content.TLabel": {
        "background": "#ffffff",  # White background
        "font": ("Arial", 16),
        "padding": 20,
        "anchor": "center",
        "justify": "center",
        "foreground": "#2c3e50"  # Dark text
    },
    "TLabel": {
        "foreground": "#2c3e50",  # Dark text
        "background": "#ffffff"   # White background
    },
    "TFrame": {
        "background": "#ffffff"   # White background
    },
    "TLabelframe": {
        "background": "#ffffff",  # White background
        "foreground": "#2c3e50"   # Dark text
    },
    "TLabelframe.Label": {
        "background": "#ffffff",  # White background
        "foreground": "#2c3e50"   # Dark text
    },
    "Main.TFrame": {
        "background": "#ffffff"  # White background
    },
    # Buttons can keep their dark backgrounds with white text
    "ShowAnswer.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "width": 30,
        "background": "#ffffff",  # White background
        "foreground": "#2c3e50",  # Dark text
        "relief": "raised",
        "borderwidth": 2
    },
    "Action.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "background": "#ffffff",  # White background
        "foreground": "#2c3e50",  # Dark text
        "relief": "raised",
        "borderwidth": 2
    },
    "Correct.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "background": "#ffffff",  # White background
        "foreground": "#2c3e50",  # Dark text
        "relief": "raised",
        "borderwidth": 2
    },
    "Wrong.TButton": {
        "font": ("Arial", 12),
        "padding": 10,
        "background": "#ffffff",  # White background
        "foreground": "#2c3e50",  # Dark text
        "relief": "raised",
        "borderwidth": 2
    },
    # Entry and Combobox styles
    "TEntry": {
        "fieldbackground": "#ffffff",
        "foreground": "#2c3e50"
    },
    "TCombobox": {
        "fieldbackground": "#ffffff",
        "foreground": "#2c3e50",
        "selectbackground": "#34495e",
        "selectforeground": "#ffffff"
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
