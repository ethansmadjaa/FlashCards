import tkinter as tk
import os
import sys
import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')

# Suppress macOS IMK messages
if sys.platform == 'darwin':  # Check if running on macOS
    # Redirect stderr to devnull
    stderr = sys.stderr
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull

from src.utils import initialize_files
from src.windows import FlashcardApp


def main():
    initialize_files()
    root = tk.Tk()
    FlashcardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
