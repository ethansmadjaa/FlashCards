import tkinter as tk
from tkinter import ttk

from ..config import STYLES


def setup_styles() -> None:
    """Initialize ttk styles"""
    style = ttk.Style()
    for name, config in STYLES.items():
        style.configure(name, **config)


class BaseWindow:
    """Base class for all windows in the application"""

    def __init__(self, parent: tk.Tk, title: str, geometry: str):
        if isinstance(parent, tk.Tk):
            # If parent is the root window, use it directly
            self.window = parent
        else:
            # For other windows, create a Toplevel
            self.window = tk.Toplevel(parent)

        self.window.title(title)
        self.window.geometry(geometry)
        setup_styles()

    def create_main_frame(self, padding: int = 20) -> ttk.Frame:
        """Create and return a main container frame"""
        frame = ttk.Frame(self.window, padding=padding)
        frame.pack(expand=True, fill="both")
        return frame

    def center_window(self) -> None:
        """Center the window on the screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
