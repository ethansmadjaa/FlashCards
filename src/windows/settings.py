import tkinter as tk
from tkinter import ttk, messagebox

from .base import BaseWindow
from ..config import SETTINGS_WINDOW_SIZE, DEFAULT_FONT_SIZE, DEFAULT_CARDS_PER_SESSION
from ..config import DEFAULT_SHOW_PROGRESS, ENABLE_SOUNDS
from ..models import Settings, save_settings


class SettingsWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Settings", SETTINGS_WINDOW_SIZE)
        self.enable_sounds_var = None
        self.preview_label = None
        self.show_progress_var = tk.BooleanVar(value=DEFAULT_SHOW_PROGRESS)
        self.cards_label = None
        self.cards_scale = None
        self.cards_per_session_var = None
        self.font_scale = None
        self.font_size_var = None
        self.settings = Settings()  # Get singleton instance
        self.setup_ui()
        self.load_current_settings()
        self.center_window()

    def setup_ui(self):
        """Set up the settings UI"""
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="⚙️ Application Settings",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        # Font Size
        self.setup_font_size_control(main_frame)

        # Cards per Session
        self.setup_cards_per_session_control(main_frame)

        # Progress Bar Toggle
        self.setup_progress_toggle(main_frame)

        # Preview Frame
        self.setup_preview_frame(main_frame)

        # Sound Settings
        self.setup_sound_settings(main_frame)

        # Action Buttons
        self.setup_action_buttons(main_frame)

    def setup_font_size_control(self, parent):
        """Setup font size control"""
        frame = ttk.LabelFrame(parent, text="Font Size", padding=10)
        frame.pack(fill='x', padx=20, pady=10)

        self.font_size_var = tk.IntVar(value=DEFAULT_FONT_SIZE)

        ttk.Label(
            frame,
            text=f"Size: {DEFAULT_FONT_SIZE}px"
        ).pack(side='left', padx=5)

        self.font_scale = ttk.Scale(
            frame,
            from_=10,
            to=20,
            orient='horizontal',
            variable=self.font_size_var,
            command=lambda e: self.update_preview()
        )
        self.font_scale.pack(side='left', fill='x', expand=True, padx=10)

    def setup_cards_per_session_control(self, parent):
        """Setup cards per session control"""
        frame = ttk.LabelFrame(parent, text="Cards per Study Session", padding=10)
        frame.pack(fill='x', padx=20, pady=10)

        self.cards_per_session_var = tk.IntVar(value=DEFAULT_CARDS_PER_SESSION)

        ttk.Label(
            frame,
            text=f"Cards: {DEFAULT_CARDS_PER_SESSION}"
        ).pack(side='left', padx=5)

        self.cards_scale = ttk.Scale(
            frame,
            from_=5,
            to=50,
            orient='horizontal',
            variable=self.cards_per_session_var,
            command=lambda e: self.update_cards_label()
        )
        self.cards_scale.pack(side='left', fill='x', expand=True, padx=10)

        self.cards_label = ttk.Label(frame, text="")
        self.cards_label.pack(side='right', padx=5)

    def setup_progress_toggle(self, parent):
        """Setup progress bar visibility toggle"""
        frame = ttk.LabelFrame(parent, text="Study Session Options", padding=10)
        frame.pack(fill='x', padx=20, pady=10)

        ttk.Checkbutton(
            frame,
            text="Show Progress Bar",
            variable=self.show_progress_var
        ).pack(padx=5)

    def setup_preview_frame(self, parent):
        """Setup preview frame"""
        frame = ttk.LabelFrame(parent, text="Preview", padding=10)
        frame.pack(fill='x', padx=20, pady=10)

        self.preview_label = ttk.Label(
            frame,
            text="Sample Text Preview",
            wraplength=400
        )
        self.preview_label.pack(pady=10)

    def setup_sound_settings(self, parent):
        """Setup sound settings controls"""
        frame = ttk.LabelFrame(parent, text="Sound Settings", padding=10)
        frame.pack(fill='x', padx=20, pady=10)

        self.enable_sounds_var = tk.BooleanVar(value=ENABLE_SOUNDS)
        ttk.Checkbutton(
            frame,
            text="Enable Sound Effects",
            variable=self.enable_sounds_var
        ).pack(padx=5)

    def setup_action_buttons(self, parent):
        """Setup save and cancel buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="💾 Save Changes",
            command=self.save_settings,
            style="Action.TButton",
            width=20
        ).pack(side='left', padx=5)

    def load_current_settings(self):
        """Load current settings"""
        self.font_size_var.set(self.settings.get('font_size', DEFAULT_FONT_SIZE))
        self.cards_per_session_var.set(self.settings.get('cards_per_session', DEFAULT_CARDS_PER_SESSION))
        self.show_progress_var.set(self.settings.get('show_progress', DEFAULT_SHOW_PROGRESS))
        self.update_preview()
        self.update_cards_label()

    def update_preview(self):
        """Update the preview text"""
        font_size = self.font_size_var.get()
        self.preview_label.configure(
            font=("Arial", font_size),
            text=f"Sample Text ({font_size}px)\nABCDEFG abcdefg 123456"
        )

    def update_cards_label(self):
        """Update cards per session label"""
        cards = self.cards_per_session_var.get()
        self.cards_label.configure(text=f"{cards} cards")

    def save_settings(self):
        """Save settings"""
        new_settings = {
            'font_size': self.font_size_var.get(),
            'cards_per_session': self.cards_per_session_var.get(),
            'show_progress': self.show_progress_var.get()
        }
        
        print(f"DEBUG: Saving settings: {new_settings}")  # Debug print

        if save_settings(new_settings):
            # Update the singleton instance
            self.settings.settings.update(new_settings)
            
            messagebox.showinfo(
                "Success",
                "✅ Settings saved successfully!\n"
                "Changes will take effect in new windows."
            )
            self.return_to_main()
        else:
            messagebox.showerror(
                "Error",
                "Failed to save settings.\n"
                "Please try again."
            )

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window)
