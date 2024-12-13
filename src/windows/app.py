import tkinter as tk
from tkinter import ttk
from typing import Optional

from .base import BaseWindow
from .cards import AddCardsWindow, CardManagerWindow
from .settings import SettingsWindow
from .study import ClassSelectionWindow
from ..config import MAIN_WINDOW_SIZE


class FlashcardApp(BaseWindow):
    def __init__(self, root: Optional[tk.Tk] = None):
        super().__init__(root, "Flashcard App", MAIN_WINDOW_SIZE)
        self.setup_main_screen()

    def setup_main_screen(self):
        """Set up the main menu screen"""
        # Clear existing widgets
        for widget in self.window.winfo_children():
            widget.destroy()

        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="✨ Flashcard App ✨",
            font=("Arial", 24, "bold")
        ).pack(pady=30)

        # Main menu buttons
        self.create_menu_buttons(main_frame)

    def create_menu_buttons(self, frame: ttk.Frame) -> None:
        """Create the main menu buttons"""
        buttons = [
            ("📖 Study Now", self.open_study_window),
            ("➕ Add Cards", self.open_add_cards),
            ("📝 Manage Cards", self.open_card_manager),
            ("⚙️ Settings", self.open_settings)
        ]

        for text, command in buttons:
            ttk.Button(
                frame,
                text=text,
                command=command,
                style="Action.TButton",
                width=30
            ).pack(pady=10)

    def open_study_window(self) -> None:
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()
        ClassSelectionWindow(self.window)

    def open_add_cards(self) -> None:
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()
        AddCardsWindow(self.window)

    def open_card_manager(self) -> None:
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()
        CardManagerWindow(self.window)

    def open_settings(self) -> None:
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()
        SettingsWindow(self.window)
