from tkinter import ttk
from typing import Optional
import random  # Make sure this is imported at the top
import tkinter.messagebox as messagebox

from .base import BaseWindow
from ..config import STUDY_WINDOW_SIZE, CLASS_SELECTION_SIZE, ENABLE_ANIMATIONS, \
    ANIMATION_DURATION, DEFAULT_CARDS_PER_SESSION
from ..models import StudyStats, Settings
from ..utils import load_cards_for_class, get_available_classes, safe_json_load, save_json, FLASHCARD_FILE


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

        # Get settings
        settings = Settings()
        cards_per_session = settings.get('cards_per_session', DEFAULT_CARDS_PER_SESSION)

        # Basic attributes
        self.wrong_btn = None
        self.correct_btn = None
        self.answer_frame = None
        self.show_answer_btn = None
        self.button_frame = None
        self.content_label = None
        self.card_frame = None
        self.progress_label = None
        self.class_name = class_name
        
        # Load and shuffle all cards
        all_cards = load_cards_for_class(class_name)
        if all_cards:
            random.shuffle(all_cards)
            # Take only the number of cards specified in settings
            self.cards = all_cards[:cards_per_session]
            print(f"DEBUG: Selected {len(self.cards)} cards from {len(all_cards)} available")
        else:
            self.cards = []

        self.current_index = 0
        self.correct_count = 0
        self.total_attempted = 0
        self.answer_showing = False

        # Check if we have cards
        if not self.cards:
            self.show_no_cards_message()
            return

        # Initialize UI
        self.setup_ui()
        self.show_current_card()

        # Bind shortcuts
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

        # Title showing current class
        ttk.Label(
            main_frame,
            text=f"📚 Studying: {self.class_name or 'All Classes'} 📚",
            font=("Arial", 20, "bold"),
            foreground="#2c3e50"
        ).pack(pady=20)

        # Progress label
        self.progress_label = ttk.Label(
            main_frame,
            text="📊 Progress: 0%",
            font=("Arial", 14),
            foreground="#34495e"
        )
        self.progress_label.pack(pady=10)

        # Card display
        self.card_frame = ttk.LabelFrame(
            main_frame,
            text="��� Question",
            padding=30,
            style="Card.TLabelframe"
        )
        self.card_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Question/Answer text
        self.content_label = ttk.Label(
            self.card_frame,
            text="",
            wraplength=900,
            justify="center",
            anchor="center",
            font=("Arial", 16),
            style="Content.TLabel"
        )
        self.content_label.pack(fill="both", expand=True, padx=30, pady=30)

        # Buttons frame
        self.button_frame = ttk.Frame(main_frame)  # Store reference
        self.button_frame.pack(pady=30)

        # Show/Hide answer button
        self.show_answer_btn = ttk.Button(
            self.button_frame,  # Use self.button_frame
            text="🔍 Show Answer (Space)",
            command=self.toggle_answer,
            style="ShowAnswer.TButton",
            width=30
        )
        self.show_answer_btn.pack(pady=15)

        # Answer buttons frame (initially hidden)
        self.answer_frame = ttk.Frame(self.button_frame)

        # Correct/Wrong buttons
        self.correct_btn = ttk.Button(
            self.answer_frame,
            text="✅ Correct (↑)",
            command=self.mark_correct,
            style="Correct.TButton",
            width=20
        )
        self.correct_btn.pack(side="left", padx=10)

        self.wrong_btn = ttk.Button(
            self.answer_frame,
            text="❌ Wrong (↓)",
            command=self.mark_wrong,
            style="Wrong.TButton",
            width=20
        )
        self.wrong_btn.pack(side="left", padx=10)

        # Add difficulty buttons
        self.difficulty_frame = ttk.Frame(self.button_frame)
        self.difficulty_frame.pack(pady=10)
        
        ttk.Label(
            self.difficulty_frame,
            text="Difficulty:",
            font=("Arial", 11)
        ).pack(side="left", padx=5)

        for diff in ['easy', 'medium', 'hard']:
            btn = ttk.Button(
                self.difficulty_frame,
                text=self.get_difficulty_emoji(diff),
                command=lambda d=diff: self.set_card_difficulty(d),
                width=10,
                style=f"{diff.capitalize()}.TButton"
            )
            btn.pack(side="left", padx=5)

        # Add hover effects
        self.add_button_hover_effects()

    def show_current_card(self):
        """Show the current card"""
        if self.current_index >= len(self.cards):
            self.show_completion_screen()
            return

        card = self.cards[self.current_index]
        progress = f"📝 Card {self.current_index + 1} of {len(self.cards)}"
        difficulty = card.get('difficulty', 'medium')
        difficulty_text = self.get_difficulty_emoji(difficulty)

        if self.answer_showing:
            content = (
                f"{progress} - {difficulty_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Question:\n{card['question']}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Answer:\n{card['answer']}"
            )
            self.show_answer_btn.configure(text="🔒 Hide Answer (Space)")
            self.answer_frame.pack()
            self.difficulty_frame.pack()
        else:
            content = (
                f"{progress} - {difficulty_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Question:\n{card['question']}"
            )
            self.show_answer_btn.configure(text="🔍 Show Answer (Space)")
            self.answer_frame.pack_forget()
            self.difficulty_frame.pack_forget()

        self.content_label.configure(text=content)

        # Update progress with emoji
        progress_pct = (self.total_attempted / len(self.cards)) * 100
        self.progress_label.configure(
            text=f"📊 Progress: {progress_pct:.1f}% ({self.total_attempted}/{len(self.cards)})"
        )

    def toggle_answer(self):
        """Toggle answer visibility with animation"""
        if not ENABLE_ANIMATIONS:
            self.answer_showing = not self.answer_showing
            self.show_current_card()
            return

        # Save current state
        current_width = self.card_frame.winfo_width()

        # Animation steps
        steps = 15
        duration = ANIMATION_DURATION // steps

        def animate_flip(step):
            if step <= steps // 2:
                # Shrinking animation
                ratio = 1 - (step / (steps / 2))
                new_width = int(current_width * ratio)
                if new_width > 0:
                    self.card_frame.configure(width=new_width)
            else:
                # Growing animation
                if step == (steps // 2) + 1:
                    # Change content at the middle of animation
                    self.answer_showing = not self.answer_showing
                    self.show_current_card()

                ratio = (step - steps / 2) / (steps / 2)
                new_width = int(current_width * ratio)
                self.card_frame.configure(width=new_width)

            if step < steps:
                self.window.after(duration, lambda: animate_flip(step + 1))
            else:
                self.card_frame.configure(width='')  # Reset width to auto

        animate_flip(1)

    def mark_card(self, correct: bool):
        """Animate card transition and mark it"""
        if not self.answer_showing:
            return

        def slide_out():
            # Get the original position and packing info
            original_info = self.card_frame.pack_info()
            button_frame_info = self.button_frame.pack_info()  # Save button frame info too

            # Switch to place geometry manager temporarily
            self.card_frame.pack_forget()
            self.button_frame.pack_forget()  # Unpack button frame

            self.card_frame.place(
                relx=0.5,
                rely=0.5,
                anchor="center",
                width=self.card_frame.winfo_width(),
                height=self.card_frame.winfo_height()
            )

            def animate_slide(step):
                if step < steps:
                    self.card_frame.place(
                        x=current_x + (dx * step),
                        rely=0.5,
                        anchor="center"
                    )
                    self.window.after(
                        ANIMATION_DURATION // steps,
                        lambda: animate_slide(step + 1)
                    )
                else:
                    # Update card state
                    if correct:
                        self.correct_count += 1
                    self.total_attempted += 1
                    self.current_index += 1
                    self.answer_showing = False

                    # Restore original packing
                    self.card_frame.place_forget()
                    self.card_frame.pack(**original_info)
                    self.button_frame.pack(**button_frame_info)  # Restore button frame

                    # Show next card
                    self.show_current_card()

            # Animation parameters
            current_x = self.card_frame.winfo_x()
            target_x = self.window.winfo_width()
            steps = 10
            dx = (target_x - current_x) // steps

            animate_slide(1)

        if ENABLE_ANIMATIONS:
            slide_out()
        else:
            if correct:
                self.correct_count += 1
            self.total_attempted += 1
            self.current_index += 1
            self.answer_showing = False
            self.show_current_card()

    def mark_correct(self):
        """Mark current card as correct with animation"""
        self.mark_card(True)

    def mark_wrong(self):
        """Mark current card as wrong with animation"""
        self.mark_card(False)

    def show_completion_screen(self):
        """Show completion screen with results"""
        # Save session stats
        stats = StudyStats()
        stats.add_session(
            self.class_name or "all_classes",
            self.total_attempted,
            self.correct_count
        )

        # Get historical stats
        class_stats = stats.get_class_stats(self.class_name or "all_classes")

        for widget in self.window.winfo_children():
            widget.destroy()

        main_frame = self.create_main_frame()

        # Current session results
        accuracy = (self.correct_count / self.total_attempted * 100) if self.total_attempted > 0 else 0
        grade, message, color = get_grade_info(accuracy)

        ttk.Label(
            main_frame,
            text="🎉 Study Session Complete! 🎉",
            font=("Arial", 24, "bold"),
            foreground="#2c3e50"
        ).pack(pady=20)

        # Current session frame
        session_frame = ttk.LabelFrame(main_frame, text="Current Session", padding=20)
        session_frame.pack(fill="x", padx=40, pady=10)

        ttk.Label(
            session_frame,
            text=(
                f"Grade: {grade}\n"
                f"Cards Studied: {self.total_attempted}\n"
                f"Correct Answers: {self.correct_count}\n"
                f"Accuracy: {accuracy:.1f}%\n\n"
                f"{message}"
            ),
            font=("Arial", 14),
            justify="center",
            foreground=color
        ).pack()

        # Historical stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Class Statistics", padding=20)
        stats_frame.pack(fill="x", padx=40, pady=10)

        ttk.Label(
            stats_frame,
            text=(
                f"Total Sessions: {class_stats['sessions']}\n"
                f"Average Accuracy: {class_stats['avg_accuracy']:.1f}%\n"
                f"Total Cards Studied: {class_stats['total_cards']}"
            ),
            font=("Arial", 14),
            justify="center"
        ).pack()

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="🔄 Study Again",
            command=lambda: self.start_new_session(),
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="🏠 Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=10)

    def start_new_session(self):
        """Start a new study session with the same class"""
        for widget in self.window.winfo_children():
            widget.destroy()
        # Create new study window (which will automatically shuffle cards)
        StudyWindow(self.window, self.class_name)

    def show_no_cards_message(self):
        """Show message when no cards are available"""
        for widget in self.window.winfo_children():
            widget.destroy()

        main_frame = self.create_main_frame()

        ttk.Label(
            main_frame,
            text=f"No flashcards found for {self.class_name or 'any class'}.\n"
                 "Please add some flashcards first!",
            font=("Arial", 14),
            justify="center"
        ).pack(expand=True)

        ttk.Button(
            main_frame,
            text="Return to Main Menu",
            command=self.return_to_main,
            width=25
        ).pack(pady=20)

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window)

    def add_button_hover_effects(self):
        """Add hover effects to buttons"""

        def on_enter(button_enter, style_enter):
            button_enter.configure(style=f"{style_enter}.Hover")

        def on_leave(button_leave, style_leave):
            button_leave.configure(style=style_leave)

        # Add hover styles
        hover_styles = {
            "ShowAnswer": {"background": "#2980b9"},  # Darker blue
            "Correct": {"background": "#218838"},  # Darker green
            "Wrong": {"background": "#c82333"}  # Darker red
        }

        for style_name, hover_colors in hover_styles.items():
            style = ttk.Style()
            style.configure(
                f"{style_name}.TButton.Hover",
                background=hover_colors["background"]
            )

        # Apply hover effects to buttons
        buttons = [
            (self.show_answer_btn, "ShowAnswer"),
            (self.correct_btn, "Correct"),
            (self.wrong_btn, "Wrong")
        ]

        for button, style in buttons:
            button.bind(
                '<Enter>',
                lambda e, b=button, s=style: on_enter(b, s)
            )
            button.bind(
                '<Leave>',
                lambda e, b=button, s=style: on_leave(b, s)
            )

    def quit_study(self):
        """Quit study session and save progress"""
        if self.total_attempted > 0:  # Only save if some cards were attempted
            # Calculate accuracy for attempted cards only
            accuracy = (self.correct_count / self.total_attempted * 100)
            
            # Save session stats for attempted cards only
            stats = StudyStats()
            stats.add_session(
                self.class_name or "all_classes",
                self.total_attempted,  # Only count attempted cards
                self.correct_count
            )

            message = (
                f"Study Session Results:\n\n"
                f"📝 Cards Studied: {self.total_attempted}/{len(self.cards)}\n"
                f"✅ Correct Answers: {self.correct_count}\n"
                f"🎯 Accuracy: {accuracy:.1f}%"
            )
        else:
            message = "No cards were studied in this session."

        if messagebox.askokcancel("Quit Study Session", message + "\n\nAre you sure you want to quit?"):
            # Return to main menu
            self.return_to_main()

    def get_difficulty_emoji(self, difficulty: str) -> str:
        """Get emoji for difficulty level"""
        emojis = {
            'easy': '🟢 Easy',
            'medium': '🟡 Medium',
            'hard': '🔴 Hard'
        }
        return emojis.get(difficulty, '🟡 Medium')

    def set_card_difficulty(self, difficulty: str) -> None:
        """Set difficulty for current card"""
        if self.current_index < len(self.cards):
            # Update card difficulty
            cards = safe_json_load(FLASHCARD_FILE, [])
            card_index = self.cards[self.current_index]  # Get current card
            
            # Find and update the card in the main deck
            for card in cards:
                if (card['question'] == card_index['question'] and 
                    card['class_name'] == card_index['class_name']):
                    card['difficulty'] = difficulty
                    break
            
            # Save updated cards
            if save_json(FLASHCARD_FILE, cards):
                # Update UI to show new difficulty
                self.show_current_card()
                self.set_status(f"Card difficulty set to {difficulty}", 2000)


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
