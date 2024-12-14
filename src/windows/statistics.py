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

        # Overall Stats Frame
        overall_frame = ttk.LabelFrame(main_frame, text="Overall Statistics", padding=20)
        overall_frame.pack(fill="x", padx=40, pady=10)

        overall_stats = self.stats.get_overall_stats()
        ttk.Label(
            overall_frame,
            text=(
                f"Total Study Sessions: {overall_stats['total_sessions']}\n"
                f"Total Cards Studied: {overall_stats['total_cards']}\n"
                f"Overall Accuracy: {overall_stats['overall_accuracy']:.1f}%\n"
                f"Classes Studied: {overall_stats['classes_studied']}"
            ),
            font=("Arial", 14),
            justify="center"
        ).pack(pady=10)

        # Class Stats
        class_stats_frame = ttk.LabelFrame(main_frame, text="Statistics by Class", padding=20)
        class_stats_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Create scrollable frame
        canvas = tk.Canvas(class_stats_frame, bg="#ffffff")
        scrollbar = ttk.Scrollbar(class_stats_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                canvas_frame, width=e.width
            )
        )

        # Create window in canvas
        canvas_frame = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        # Configure canvas and scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Add class statistics
        if not self.stats.stats:
            ttk.Label(
                scrollable_frame,
                text="No study sessions recorded yet.\nComplete some study sessions to see statistics!",
                font=("Arial", 12),
                justify="center"
            ).pack(pady=20)
        else:
            for class_name in sorted(self.stats.stats.keys()):
                class_frame = ttk.LabelFrame(
                    scrollable_frame,
                    text=f"📚 {class_name}",
                    padding=10
                )
                class_frame.pack(fill="x", padx=5, pady=5)

                stats = self.stats.get_class_stats(class_name)
                grade, message, color = get_grade_info(stats['avg_accuracy'])

                ttk.Label(
                    class_frame,
                    text=(
                        f"Grade: {grade}\n"
                        f"Sessions Completed: {stats['sessions']}\n"
                        f"Average Accuracy: {stats['avg_accuracy']:.1f}%\n"
                        f"Total Cards Studied: {stats['total_cards']}\n"
                        f"{message}"
                    ),
                    font=("Arial", 12),
                    foreground=color,
                    justify="center"
                ).pack(pady=5)

        # Return button
        ttk.Button(
            main_frame,
            text="🏠 Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=25
        ).pack(pady=20)

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window)
