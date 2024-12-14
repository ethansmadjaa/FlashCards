import tkinter as tk
from tkinter import ttk

from .base import BaseWindow
from ..config import SETTINGS_WINDOW_SIZE
from ..models import StudyStats


def get_grade_info(accuracy):
    """Get grade information based on accuracy"""
    if accuracy >= 90:
        return "A+", "Outstanding performance! 🌟", "#28a745"
    elif accuracy >= 80:
        return "A", "Excellent work! 🎯", "#218838"
    elif accuracy >= 70:
        return "B", "Good progress! 💪", "#17a2b8"
    elif accuracy >= 60:
        return "C", "Keep practicing! 📚", "#ffc107"
    else:
        return "D", "More study needed 💡", "#dc3545"


class StatisticsWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Study Statistics", SETTINGS_WINDOW_SIZE)
        self.stats = StudyStats()
        self.setup_ui()

    def setup_ui(self):
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="📊 Study Statistics",
            font=("Arial", 24, "bold"),
            foreground="#2c3e50"
        ).pack(pady=20)

        # Create container for scrollable content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create scrollable frame for class groups
        canvas = tk.Canvas(content_frame, bg="#ffffff")
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Get grouped statistics
        grouped_stats = self.stats.get_overall_stats()

        # Add statistics for each class group
        for base_class, stats in sorted(grouped_stats.items()):
            class_frame = ttk.LabelFrame(
                scrollable_frame,
                text=f"📚 {base_class.title()}",
                padding=20
            )
            class_frame.pack(fill="x", padx=20, pady=10)

            accuracy = stats['overall_accuracy']
            grade, message, color = get_grade_info(accuracy)

            ttk.Label(
                class_frame,
                text=(
                    f"Grade: {grade}\n"
                    f"Total Sessions: {stats['total_sessions']}\n"
                    f"Cards Studied: {stats['total_cards']}\n"
                    f"Overall Accuracy: {accuracy:.1f}%\n"
                    f"Related Classes: {stats['related_classes']}\n"
                    f"{message}"
                ),
                font=("Arial", 12),
                foreground=color,
                justify="center"
            ).pack(pady=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Return button in a separate frame at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=20)

        ttk.Button(
            button_frame,
            text="🏠 Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=25
        ).pack(anchor="center")

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window)
