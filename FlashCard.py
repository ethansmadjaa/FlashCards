import tkinter as tk

from src.utils import initialize_files
from src.windows import FlashcardApp


def main():
    initialize_files()
    root = tk.Tk()
    FlashcardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
