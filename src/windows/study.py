import random
from tkinter import ttk, messagebox
from typing import Optional

from .base import BaseWindow
from ..config import STUDY_WINDOW_SIZE, CLASS_SELECTION_SIZE
from ..utils import load_cards_for_class, get_available_classes


def get_grade_info(accuracy):
    """Get grade information based on accuracy"""
    if accuracy >= 90:
        return "A+", "Outstanding! You're mastering this material!", "#28a745"
    elif accuracy >= 80:
        return "A", "Excellent work! Keep it up!", "#218838"
    elif accuracy >= 70:
        return "B", "Good job! Room for improvement!", "#17a2b8"
    elif accuracy >= 60:
        return "C", "Not bad! Keep practicing!", "#ffc107"
    else:
        return "D", "Keep studying! You'll get there!", "#dc3545"


class StudyWindow(BaseWindow):
    def __init__(self, parent, class_name: str = None):
        super().__init__(parent, f"Study: {class_name or 'All Classes'}", STUDY_WINDOW_SIZE)

        # Initialize all instance attributes
        self.progress_label = None
        self.progress_bar = None
        self.card_frame = None
        self.content_label = None
        self.show_answer_btn = None
        self.answer_frame = None

        # Study session attributes
        self.class_name = class_name
        self.cards = load_cards_for_class(class_name)
        self.current_index = 0
        self.correct_count = 0
        self.total_attempted = 0
        self.answer_showing = False

        # Initialize UI if we have cards
        if not self.cards:
            self.show_no_cards_message()
            return

        # Shuffle cards at start
        random.shuffle(self.cards)

        # Setup UI and start session
        self.setup_ui()
        self.show_current_card()
        self.center_window()

        # Bind keyboard shortcuts
        self.window.bind('<space>', lambda e: self.toggle_answer())
        self.window.bind('<Up>', lambda e: self.mark_correct())
        self.window.bind('<Down>', lambda e: self.mark_wrong())

    def setup_ui(self):
        """Set up the main UI components"""
        main_frame = self.create_main_frame()

        # Add quit button at the top right
        quit_frame = ttk.Frame(main_frame)
        quit_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(
            quit_frame,
            text="❌ Quit Study",
            command=self.quit_study,
            style="Action.TButton",
            width=15
        ).pack(side="right", padx=10)

        # Progress frame
        self.setup_progress_bar(main_frame)

        # Card frame with proper centering
        self.card_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        self.card_frame.pack(expand=True, fill="both", pady=20)

        # Create an inner frame for better content centering
        content_frame = ttk.Frame(self.card_frame)
        content_frame.pack(expand=True, fill="both")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Card content with grid for center alignment
        self.content_label = ttk.Label(
            content_frame,
            text="",
            style="Card.TLabel",
            wraplength=700,
            justify="center",
            anchor="center"
        )
        self.content_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        # Show Answer button
        self.show_answer_btn = ttk.Button(
            button_frame,
            text="🔍 Show Answer (Space)",
            command=self.toggle_answer,
            style="Action.TButton",
            width=30
        )
        self.show_answer_btn.pack(pady=10)

        # Answer buttons frame
        self.answer_frame = ttk.Frame(button_frame)

        # Correct/Wrong buttons
        ttk.Button(
            self.answer_frame,
            text="✅ Correct (↑)",
            command=self.mark_correct,
            style="Correct.TButton",
            width=25
        ).pack(side="left", padx=10)

        ttk.Button(
            self.answer_frame,
            text="❌ Wrong (↓)",
            command=self.mark_wrong,
            style="Wrong.TButton",
            width=25
        ).pack(side="left", padx=10)

    def setup_progress_bar(self, frame):
        """Set up the progress tracking UI"""
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill="x", pady=(0, 20))

        self.progress_label = ttk.Label(
            progress_frame,
            text="Progress: 0%",
            font=("Arial", 10)
        )
        self.progress_label.pack(side="top", pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=700
        )
        self.progress_bar.pack(fill="x")

    def show_no_cards_message(self):
        """Display message when no cards are available"""
        self.window.geometry("400x200")
        ttk.Label(
            self.window,
            text=f"No flashcards found for {self.class_name or 'any class'}\n"
                 "Please add some flashcards first!",
            font=("Arial", 12),
            justify="center"
        ).pack(expand=True)

    def show_current_card(self):
        """Display the current card"""
        if self.current_index >= len(self.cards):
            self.show_completion_screen()
            return

        card = self.cards[self.current_index]
        card_count = f"Card {self.current_index + 1} of {len(self.cards)}"

        if self.answer_showing:
            self.content_label.config(
                text=f"📝 {card_count}\n\n"
                     f"❓ Question:\n{card['question']}\n\n"
                     f"💡 Answer:\n{card['answer']}"
            )
            self.answer_frame.pack()
        else:
            self.content_label.config(
                text=f"📝 {card_count}\n\n"
                     f"❓ Question:\n{card['question']}"
            )
            self.answer_frame.pack_forget()

        self.update_progress()

    def toggle_answer(self):
        """Toggle the answer visibility"""
        self.answer_showing = not self.answer_showing
        self.show_current_card()

    def mark_correct(self):
        """Mark current card as correct"""
        if not self.answer_showing:
            return
        self.correct_count += 1
        self.total_attempted += 1
        self.next_card()

    def mark_wrong(self):
        """Mark current card as wrong"""
        if not self.answer_showing:
            return
        self.total_attempted += 1
        self.next_card()

    def next_card(self):
        """Move to the next card"""
        self.current_index += 1
        self.answer_showing = False
        self.show_current_card()

    def update_progress(self):
        """Update the progress bar and label"""
        progress = (self.total_attempted / len(self.cards)) * 100
        self.progress_bar["value"] = progress
        self.progress_label.config(
            text=f"Progress: {progress:.1f}% "
                 f"({self.total_attempted}/{len(self.cards)} cards)"
        )

    def show_completion_screen(self):
        """Show the study session completion screen"""
        # Clear main UI
        for widget in self.window.winfo_children():
            widget.destroy()

        completion_frame = self.create_main_frame()

        # Calculate score and determine grade
        accuracy = (self.correct_count / self.total_attempted * 100) if self.total_attempted else 0
        grade, message, color = get_grade_info(accuracy)

        # Display grade
        ttk.Label(
            completion_frame,
            text=grade,
            font=("Arial", 72, "bold"),
            foreground=color
        ).pack(pady=(0, 20))

        # Display results
        results_text = (
            f"📊 Session Complete!\n\n"
            f"📝 Cards Studied: {self.total_attempted}\n"
            f"✅ Correct Answers: {self.correct_count}\n"
            f"🎯 Accuracy: {accuracy:.1f}%\n\n"
            f"{message}\n\n"
            f"{'⭐ ' * (int(accuracy / 20) + 1)}"
        )

        ttk.Label(
            completion_frame,
            text=results_text,
            font=("Arial", 14),
            justify="center",
            wraplength=600
        ).pack(pady=20)

        # Action buttons
        button_frame = ttk.Frame(completion_frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="🔄 Study Again",
            command=self.restart_study,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="✅ Finish",
            command=self.window.destroy,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=10)

    def restart_study(self):
        """Restart the study session"""
        self.current_index = 0
        self.correct_count = 0
        self.total_attempted = 0
        self.answer_showing = False
        random.shuffle(self.cards)

        # Clear and recreate UI
        for widget in self.window.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.show_current_card()

    def quit_study(self):
        """Show results and quit study session"""
        if self.total_attempted > 0:
            accuracy = (self.correct_count / self.total_attempted * 100)
            message = (
                f"Study Session Results:\n\n"
                f"📝 Cards Studied: {self.total_attempted}/{len(self.cards)}\n"
                f"✅ Correct Answers: {self.correct_count}\n"
                f"🎯 Accuracy: {accuracy:.1f}%"
            )
        else:
            message = "No cards were studied in this session."

        if messagebox.askokcancel("Quit Study Session", message + "\n\nAre you sure you want to quit?"):
            # Clear window and return to main menu
            for widget in self.window.winfo_children():
                widget.destroy()
            from .app import FlashcardApp  # Import here to avoid circular import
            FlashcardApp(self.window)


class ClassSelectionWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Select Class to Study", CLASS_SELECTION_SIZE)

        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        """Set up the class selection UI"""
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="📚 Select Class to Study",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 30))

        # Get available classes
        classes = sorted(get_available_classes())

        if not classes:
            ttk.Label(
                main_frame,
                text="No classes found!\nPlease add some flashcards first.",
                font=("Arial", 12),
                justify="center"
            ).pack(expand=True)

            ttk.Button(
                main_frame,
                text="↩️ Return to Main Menu",
                command=self.return_to_main,
                style="Action.TButton",
                width=25
            ).pack(pady=20)
            return

        # Class buttons
        ttk.Button(
            main_frame,
            text="📚 Study All Classes",
            command=lambda: self.start_study(None),
            style="Action.TButton",
            width=30
        ).pack(pady=10)

        ttk.Label(
            main_frame,
            text="- or select a specific class -",
            font=("Arial", 10)
        ).pack(pady=10)

        # Create a frame for class buttons with scrollbar if needed
        class_frame = ttk.Frame(main_frame)
        class_frame.pack(expand=True, fill="both", padx=20)

        for class_name in classes:
            ttk.Button(
                class_frame,
                text=f"📖 {class_name}",
                command=lambda c=class_name: self.start_study(c),
                style="Action.TButton",
                width=30
            ).pack(pady=5)

        # Return button
        ttk.Button(
            main_frame,
            text="↩️ Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=25
        ).pack(pady=20)

    def start_study(self, class_name: Optional[str]):
        """Start study session with selected class"""
        for widget in self.window.winfo_children():
            widget.destroy()
        StudyWindow(self.window, class_name)

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window)
