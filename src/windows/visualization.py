import tkinter as tk
from tkinter import ttk
from .base import BaseWindow
from ..config import SETTINGS_WINDOW_SIZE
from ..models import StudyStats
from ..visualization import ProgressVisualization

class VisualizationWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Progress Visualization", SETTINGS_WINDOW_SIZE)
        self.stats = StudyStats()
        self.setup_ui()

    def setup_ui(self):
        """Setup the visualization UI"""
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="📊 Progress Visualization",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # Accuracy over time tab
        accuracy_frame = ttk.Frame(notebook)
        notebook.add(accuracy_frame, text="Accuracy Trends")

        # Class performance tab
        performance_frame = ttk.Frame(notebook)
        notebook.add(performance_frame, text="Class Performance")

        # Study frequency tab
        frequency_frame = ttk.Frame(notebook)
        notebook.add(frequency_frame, text="Study Frequency")

        # New learning analysis tabs
        learning_frame = ttk.Frame(notebook)
        notebook.add(learning_frame, text="Learning Curves")

        retention_frame = ttk.Frame(notebook)
        notebook.add(retention_frame, text="Retention Analysis")

        # Create visualizations
        viz = ProgressVisualization(self.stats.stats)
        viz.create_accuracy_over_time(accuracy_frame)
        viz.create_class_performance(performance_frame)
        viz.create_study_frequency(frequency_frame)
        viz.create_learning_curve(learning_frame)
        viz.create_retention_analysis(retention_frame)

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