import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
import json
import os
from datetime import datetime, timedelta

# File to store flashcards
FLASHCARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flashcards.json")


def initialize_files():
    """Initialize necessary files if they don't exist"""
    # Initialize flashcards.json
    if not os.path.exists(FLASHCARD_FILE):
        with open(FLASHCARD_FILE, "w") as f:
            json.dump([], f)

    # Initialize settings.json
    if not os.path.exists("settings.json"):
        default_settings = {
            "font_size": 12,
            "cards_per_session": 20,
            "show_progress": True
        }
        with open("settings.json", "w") as f:
            json.dump(default_settings, f)


def safe_json_load(file_path, default_value):
    """Safely load JSON file with error handling"""
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Error loading {file_path}: {str(e)}")
        return default_value


class AddCardsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Add Flashcards")
        self.window.geometry("800x700")  # Increased add cards window size

        # Main container
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True, fill="both")

        # Title
        ttk.Label(
            main_frame,
            text="✨  Add New Flashcard  ✨",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))

        # Class selection
        ttk.Label(
            main_frame,
            text="Select Class : ",
            font=("Arial", 12)
        ).pack()

        self.class_var = tk.StringVar()
        self.class_combobox = ttk.Combobox(
            main_frame,
            textvariable=self.class_var,
            width=40,
            font=("Arial", 11)
        )
        self.update_class_list()
        self.class_combobox.pack(pady=(0, 15))

        # Center the new class entry and button
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill="x", pady=(0, 20))

        # Add a spacer frame on the left
        ttk.Frame(entry_frame).pack(side="left", expand=True)

        # New class entry
        self.new_class_entry = ttk.Entry(
            entry_frame,
            width=30,
            font=("Arial", 11)
        )
        self.new_class_entry.pack(side="left")

        # Add New Class button
        ttk.Button(
            entry_frame,
            text="➕  Add New Class",
            command=self.add_new_class,
            width=20
        ).pack(side="left", padx=5)

        # Add a spacer frame on the right
        ttk.Frame(entry_frame).pack(side="left", expand=True)

        # Question
        ttk.Label(
            main_frame,
            text="Question : ",
            font=("Arial", 12)
        ).pack()

        self.question_entry = scrolledtext.ScrolledText(
            main_frame,
            width=50,
            height=5,
            font=("Arial", 11),
            wrap=tk.WORD  # Enable word wrapping
        )
        self.question_entry.pack(pady=(0, 15))

        # Answer
        ttk.Label(
            main_frame,
            text="Answer : ",
            font=("Arial", 12)
        ).pack()

        self.answer_entry = scrolledtext.ScrolledText(
            main_frame,
            width=50,
            height=5,
            font=("Arial", 11),
            wrap=tk.WORD  # Enable word wrapping
        )
        self.answer_entry.pack(pady=(0, 20))

        # Add button
        ttk.Button(
            main_frame,
            text="💾  Save Flashcard",
            command=self.add_flashcard,
            width=25
        ).pack()

    def update_class_list(self):
        classes = set()
        flashcards = safe_json_load(FLASHCARD_FILE, [])
        for card in flashcards:
            if "class_name" in card:
                classes.add(card["class_name"])
        self.class_combobox['values'] = sorted(list(classes))

    def add_flashcard(self):
        question = self.question_entry.get("1.0", tk.END).strip()
        answer = self.answer_entry.get("1.0", tk.END).strip()
        class_name = self.class_var.get().strip()

        if not class_name:
            messagebox.showwarning(
                "Input Error",
                "❌  Please select or add a class first !"
            )
            return

        if question and answer:
            flashcards = []
            if os.path.exists(FLASHCARD_FILE):
                with open(FLASHCARD_FILE, "r") as file:
                    flashcards = json.load(file)

            # Format the card data
            new_card = {
                "question": question,
                "answer": answer,
                "class_name": class_name,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            flashcards.append(new_card)

            with open(FLASHCARD_FILE, "w") as file:
                json.dump(flashcards, file, indent=4)  # Added indentation for better formatting

            messagebox.showinfo(
                "Success",
                "✅  Flashcard added successfully !\n\n"
                f"Class : {class_name}\n"
                f"Question Length : {len(question)} characters\n"
                f"Answer Length : {len(answer)} characters"
            )

            # Clear entries and update
            self.update_class_list()
            self.question_entry.delete("1.0", tk.END)
            self.answer_entry.delete("1.0", tk.END)
            self.question_entry.focus()
        else:
            messagebox.showwarning(
                "Input Error",
                "❌  Please enter both a question and an answer !"
            )

    def add_new_class(self):
        new_class = self.new_class_entry.get().strip()
        if new_class:
            current_values = list(self.class_combobox['values'])
            if new_class not in current_values:
                current_values.append(new_class)
                self.class_combobox['values'] = sorted(current_values)
                self.class_var.set(new_class)
                self.new_class_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Info", "This class already exists!")
        else:
            messagebox.showwarning("Input Error", "Please enter a class name.")


class StudyWindow:
    def __init__(self, parent, class_name=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Study: {class_name}")

        self.class_name = class_name
        self.flashcards = []
        self.current_card_index = 0
        self.answer_showing = False
        self.correct_count = 0
        self.total_attempted = 0

        # Load cards first
        self.load_flashcards()

        # Check if we have cards
        if not self.flashcards:
            # Show no cards message in the existing window
            self.window.geometry("400x200")
            ttk.Label(
                self.window,
                text=f"No flashcards found for class: {class_name}\nPlease add some flashcards first!",
                font=("Arial", 12),
                justify="center"
            ).pack(expand=True)
            return

        # If we have cards, set up the full UI
        self.window.geometry("800x700")  # Made taller for progress bar

        # Main container with padding and style
        self.main_container = ttk.Frame(self.window, padding=20)
        self.main_container.pack(expand=True, fill="both")

        # Progress bar frame
        self.progress_frame = ttk.Frame(self.main_container)
        self.progress_frame.pack(fill='x', pady=(0, 20))

        # Progress label
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="Progress: 0%",
            font=("Arial", 10)
        )
        self.progress_label.pack(side='top', pady=(0, 5))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            length=700
        )
        self.progress_bar.pack(fill='x')

        # Card frame with border and padding
        self.card_frame = ttk.Frame(self.main_container, relief="solid", borderwidth=1)
        self.card_frame.pack(expand=True, fill="both", pady=20)

        # Card content frame
        self.content_frame = ttk.Frame(self.card_frame, padding=20)
        self.content_frame.pack(expand=True, fill="both")

        # Card display with better styling
        self.display_label = ttk.Label(
            self.content_frame,
            text="Loading cards...",
            font=("Arial", 16),
            wraplength=700,
            justify="center",
            style="Card.TLabel"
        )
        self.display_label.pack(expand=True)

        # Button frame with better spacing
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(pady=20)

        # Show Answer button with style
        self.show_answer_btn = ttk.Button(
            self.button_frame,
            text="🔍  Show Answer  (Space)",
            command=self.toggle_answer,
            width=30,
            style="Action.TButton"
        )
        self.show_answer_btn.pack(pady=10)

        # Answer buttons frame
        self.answer_frame = ttk.Frame(self.button_frame)

        # Styled buttons
        self.correct_button = ttk.Button(
            self.answer_frame,
            text="✅  Correct  (↑)",
            command=self.mark_correct,
            width=25,
            style="Correct.TButton"
        )
        self.correct_button.pack(side="left", padx=10)

        self.wrong_button = ttk.Button(
            self.answer_frame,
            text="❌  Wrong  (↓)",
            command=self.mark_wrong,
            width=25,
            style="Wrong.TButton"
        )
        self.wrong_button.pack(side="left", padx=10)

        # Create custom styles
        self.create_styles()

        # Key bindings
        self.window.bind('<space>', lambda e: self.toggle_answer())
        self.window.bind('<Up>', lambda e: self.mark_correct())
        self.window.bind('<Down>', lambda e: self.mark_wrong())

        # Initialize card tracking
        self.total_cards = len(self.flashcards)
        # Show first card
        self.show_current_card()

    def create_styles(self):
        # Create custom styles for widgets
        style = ttk.Style()

        # Card label style
        style.configure(
            "Card.TLabel",
            background="#f8f9fa",
            padding=20,
            font=("Arial", 16)
        )

        # Button styles
        style.configure(
            "Action.TButton",
            font=("Arial", 12),
            padding=10
        )

        style.configure(
            "Correct.TButton",
            font=("Arial", 12),
            padding=10,
            background="#28a745"
        )

        style.configure(
            "Wrong.TButton",
            font=("Arial", 12),
            padding=10,
            background="#dc3545"
        )

    def update_progress(self):
        progress = (self.total_attempted / len(self.flashcards)) * 100
        self.progress_bar['value'] = progress
        self.progress_label.config(
            text=f"Progress: {progress:.1f}% ({self.total_attempted}/{len(self.flashcards)} cards)"
        )

    def load_flashcards(self):
        try:
            # Debug: Print current working directory and full file path
            print(f"Current directory: {os.getcwd()}")
            print(f"Looking for file: {os.path.abspath(FLASHCARD_FILE)}")

            if not os.path.exists(FLASHCARD_FILE):
                print(f"Error: {FLASHCARD_FILE} not found!")
                self.flashcards = []
                return

            with open(FLASHCARD_FILE, "r", encoding='utf-8') as file:
                all_flashcards = json.load(file)
                print(f"Loading cards for class: {self.class_name}")
                print(f"Total cards in file: {len(all_flashcards)}")

                # Filter cards for this class
                self.flashcards = [
                    card for card in all_flashcards
                    if card.get("class_name", "").lower() == self.class_name.lower()  # Case-insensitive comparison
                ]

                if self.flashcards:
                    print(f"Found {len(self.flashcards)} cards for class {self.class_name}")
                    print(f"First card: {self.flashcards[0]}")
                else:
                    print(f"No cards found for class: {self.class_name}")

        except Exception as e:
            print(f"Error loading flashcards: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full error traceback
            self.flashcards = []

    def show_current_card(self):
        if not self.flashcards:
            self.display_label.config(
                text=f"No flashcards found for class: {self.class_name}\n"
                     "Please add some flashcards first!"
            )
            return

        try:
            current_card = self.flashcards[self.current_card_index]
            card_count = f"Card {self.current_card_index + 1} of {len(self.flashcards)}"

            if self.answer_showing:
                self.display_label.config(
                    text=f"📝  {card_count}\n\n"
                         f"❓  Question:\n{current_card['question']}\n\n"
                         f"💡  Answer:\n{current_card['answer']}"
                )
                self.answer_frame.pack()
            else:
                self.display_label.config(
                    text=f"📝  {card_count}\n\n"
                         f"❓  Question:\n{current_card['question']}"
                )
                self.answer_frame.pack_forget()

            # Update progress bar
            self.update_progress()

        except Exception as e:
            print(f"Error showing card: {str(e)}")
            self.display_label.config(text="Error displaying card")

    def toggle_answer(self):
        self.answer_showing = not self.answer_showing
        self.show_current_card()
        if self.answer_showing:
            self.answer_frame.pack(pady=10)  # Show correct/wrong buttons
        else:
            self.answer_frame.pack_forget()  # Hide correct/wrong buttons

    def mark_correct(self):
        if not self.answer_showing:
            return
        self.correct_count += 1
        self.total_attempted += 1
        self.next_card()

    def mark_wrong(self):
        if not self.answer_showing:
            return
        self.total_attempted += 1
        self.next_card()

    def next_card(self):
        self.current_card_index += 1  # Just increment, don't cycle
        self.answer_showing = False
        self.answer_frame.pack_forget()

        # Check if we've completed all cards
        if self.current_card_index >= len(self.flashcards):
            self.show_completion_screen()
        else:
            self.show_current_card()

    def show_completion_screen(self):
        # Clear the main UI elements
        self.progress_frame.pack_forget()
        self.card_frame.pack_forget()
        self.button_frame.pack_forget()

        # Calculate accuracy
        accuracy = (self.correct_count / self.total_attempted) * 100 if self.total_attempted > 0 else 0

        # Create completion frame
        completion_frame = ttk.Frame(self.main_container, padding=20)
        completion_frame.pack(expand=True, fill="both")

        # Determine grade and message
        if accuracy >= 90:
            grade = "🏆  OUTSTANDING !  🌟"
            message = "You're absolutely crushing it! Keep up the amazing work!"
            color = "#28a745"
            grade_letter = "A+"
        elif accuracy >= 80:
            grade = "🎉  EXCELLENT !  🌟"
            message = "Fantastic performance! Just a bit more to perfection!"
            color = "#218838"
            grade_letter = "A"
        elif accuracy >= 70:
            grade = "👍  GREAT WORK !  💫"
            message = "You're doing really well! Keep practicing!"
            color = "#17a2b8"
            grade_letter = "B"
        elif accuracy >= 60:
            grade = "💪  GOOD EFFORT !  ✨"
            message = "Nice progress! Keep pushing forward!"
            color = "#ffc107"
            grade_letter = "C"
        else:
            grade = "📚  KEEP GOING !  💫"
            message = "Every mistake is a learning opportunity! Don't give up!"
            color = "#dc3545"
            grade_letter = "D"

        # Grade display
        grade_label = ttk.Label(
            completion_frame,
            text=f"{grade_letter}",
            font=("Arial", 72, "bold"),
            foreground=color
        )
        grade_label.pack(pady=(0, 20))

        # Results text
        results_text = (
            f"{grade}\n\n"
            f"📊  Session Complete!\n\n"
            f"📝  Cards Studied: {self.total_attempted}\n"
            f"✅  Correct Answers: {self.correct_count}\n"
            f"🎯  Accuracy: {accuracy:.1f}%\n\n"
            f"{message}\n\n"
            f"{'⭐ ' * (int(accuracy / 20) + 1)}"
        )

        results_label = ttk.Label(
            completion_frame,
            text=results_text,
            font=("Arial", 14),
            justify="center",
            wraplength=600
        )
        results_label.pack(pady=20)

        # Buttons frame
        button_frame = ttk.Frame(completion_frame)
        button_frame.pack(pady=20)

        # Study Again button
        ttk.Button(
            button_frame,
            text="🔄  Study Again",
            command=self.restart_study,
            width=20,
            style="Action.TButton"
        ).pack(side="left", padx=10)

        # Finish button
        ttk.Button(
            button_frame,
            text="✅  Finish",
            command=self.window.destroy,
            width=20,
            style="Action.TButton"
        ).pack(side="left", padx=10)

    def restart_study(self):
        self.current_card_index = 0
        self.correct_count = 0
        self.total_attempted = 0
        self.answer_showing = False

        # Reset display
        self.display_frame.pack(expand=True, fill="both", pady=20)
        self.button_frame.pack(fill="x", pady=10)
        self.show_answer_btn.pack(pady=10)

        # Shuffle cards and start over
        import random
        random.shuffle(self.flashcards)
        self.show_flashcard()


class ClassSelectionWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Select Class to Study")
        self.window.geometry("600x700")  # Increased class selection window size

        # Title
        ttk.Label(
            self.window,
            text="Select a Class",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        # Get available classes
        self.classes = self.get_available_classes()

        # Create buttons for each class
        for class_name in sorted(self.classes):
            ttk.Button(
                self.window,
                text=class_name,
                command=lambda c=class_name: self.start_study(c),
                width=30
            ).pack(pady=5)

        # Add "All Classes" button
        ttk.Button(
            self.window,
            text="Study All Classes",
            command=lambda: self.start_study(None),
            width=30
        ).pack(pady=20)

    def get_available_classes(self):
        classes = set()
        try:
            print(f"Looking for flashcards file at: {os.path.abspath(FLASHCARD_FILE)}")
            if os.path.exists(FLASHCARD_FILE):
                with open(FLASHCARD_FILE, "r", encoding='utf-8') as file:
                    flashcards = json.load(file)
                    print(f"Found {len(flashcards)} cards in file")
                    for card in flashcards:
                        if "class_name" in card:
                            class_name = card["class_name"]
                            classes.add(class_name)
                            print(f"Found class: {class_name}")
        except Exception as e:
            print(f"Error reading classes: {str(e)}")
            import traceback
            traceback.print_exc()

        print(f"Available classes: {classes}")
        return classes

    def start_study(self, class_name):
        print(f"Starting study for class: {class_name}")  # Debug print
        self.window.destroy()
        StudyWindow(self.window.master, class_name)


class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard App")
        self.root.geometry("800x600")  # Increased main window size

        # Initialize files
        initialize_files()

        # Main container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill="both")

        # Title with emoji
        ttk.Label(
            main_frame,
            text="📚  Study Smart !  🎯",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        # Buttons
        buttons = [
            ("➕  Add Cards", self.open_add_cards),
            ("📖  Study Now", self.open_study_window),
            ("📝  Manage Cards", self.open_card_manager),
            ("⚙️  Settings", self.open_settings)
        ]

        for text, command in buttons:
            ttk.Button(
                main_frame,
                text=text,
                command=command,
                width=30
            ).pack(pady=10)

    def open_add_cards(self):
        AddCardsWindow(self.root)

    def open_study_window(self):
        # Open class selection window first
        self.open_class_selection()

    def open_class_selection(self):
        class_window = tk.Toplevel(self.root)
        class_window.title("Select Class")
        class_window.geometry("600x500")  # Increased class selection window size

        main_frame = ttk.Frame(class_window, padding=20)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(
            main_frame,
            text="📚  Select a Class  📚",
            font=("Arial", 14, "bold")
        ).pack(pady=20)

        # Get available classes
        classes = set()
        if os.path.exists(FLASHCARD_FILE):
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)
                for card in flashcards:
                    if "class_name" in card:
                        classes.add(card["class_name"])

        # Create buttons for each class
        for class_name in sorted(classes):
            ttk.Button(
                main_frame,
                text=f"📖  {class_name}",
                command=lambda c=class_name: self.start_study_session(c, class_window),
                width=30
            ).pack(pady=5)

    def start_study_session(self, class_name, class_window):
        class_window.destroy()
        StudyWindow(self.root, class_name)

    def open_card_manager(self):
        CardManagerWindow(self.root)

    def open_settings(self):
        SettingsWindow(self.root)


class CardManagerWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Flashcards")
        self.window.geometry("1000x600")  # Made window larger

        # Add search and filter options
        self.search_frame = ttk.Frame(self.window)
        self.search_frame.pack(fill='x', pady=10, padx=10)

        # Add class filter
        ttk.Label(self.search_frame, text="Filter by Class:").pack(side='left', padx=5)
        self.class_var = tk.StringVar()
        self.class_filter = ttk.Combobox(
            self.search_frame,
            textvariable=self.class_var,
            width=20
        )
        self.class_filter.pack(side='left', padx=5)

        # Search bar
        ttk.Label(self.search_frame, text="Search:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)

        self.search_button = ttk.Button(
            self.search_frame,
            text="Search",
            command=self.search_cards
        )
        self.search_button.pack(side='left', padx=5)

        # Clear search button
        self.clear_button = ttk.Button(
            self.search_frame,
            text="Clear Search",
            command=self.clear_search
        )
        self.clear_button.pack(side='left', padx=5)

        # Create frame for treeview and scrollbars
        self.tree_frame = ttk.Frame(self.window)
        self.tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Add treeview with both scrollbars
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=('Class', 'Question', 'Answer'),
            show='headings',
            selectmode='browse'  # Single selection mode
        )

        # Add scrollbars
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Configure column headings with sorting
        for col in ('Class', 'Question', 'Answer'):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=300, minwidth=150)

        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.hsb.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        # Button frame
        self.button_frame = ttk.Frame(self.window)
        self.button_frame.pack(fill='x', padx=10, pady=10)

        # Add control buttons with better icons
        ttk.Button(
            self.button_frame,
            text="🗑️ Delete Selected",
            command=self.delete_selected
        ).pack(side='left', padx=5)

        ttk.Button(
            self.button_frame,
            text="✏️ Edit Selected",
            command=self.edit_selected
        ).pack(side='left', padx=5)

        # Load initial data and update class filter
        self.load_cards()
        self.update_class_filter()

        # Bind events
        self.search_entry.bind('<Return>', lambda e: self.search_cards())
        self.class_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_by_class())
        self.tree.bind('<Double-1>', lambda e: self.edit_selected())

    def update_class_filter(self):
        classes = set()
        for item in self.tree.get_children():
            class_name = self.tree.item(item)['values'][0]
            if class_name:
                classes.add(class_name)
        self.class_filter['values'] = ['All Classes'] + sorted(list(classes))
        self.class_filter.set('All Classes')

    def filter_by_class(self):
        selected_class = self.class_var.get()
        search_term = self.search_entry.get().lower()

        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            class_match = selected_class == 'All Classes' or values[0] == selected_class
            search_match = not search_term or any(search_term in str(v).lower() for v in values)

            if class_match and search_match:
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.class_filter.set('All Classes')
        self.load_cards()

    def sort_treeview(self, col):
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()

        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

    def load_cards(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load cards with error handling
        flashcards = safe_json_load(FLASHCARD_FILE, [])
        for i, card in enumerate(flashcards):
            try:
                self.tree.insert(
                    '',
                    'end',
                    values=(
                        card.get('class_name', ''),
                        card.get('question', ''),
                        card.get('answer', '')
                    ),
                    iid=str(i)
                )
            except Exception as e:
                print(f"Error loading card {i}: {str(e)}")

    def search_cards(self):
        search_term = self.search_entry.get().lower()
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.tree.selection_add(item)
            else:
                self.tree.selection_remove(item)

    def delete_selected(self):
        if not self.tree.selection():
            messagebox.showinfo("Info", "ℹ️  Please select a card to delete")
            return

        if messagebox.askyesno("Confirm Delete", "🗑️  Are you sure you want to delete the selected card(s) ?"):
            # Load current cards
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)

            # Get indices to delete
            indices = [int(i) for i in self.tree.selection()]
            # Remove cards in reverse order to maintain correct indices
            for index in sorted(indices, reverse=True):
                flashcards.pop(index)

            # Save updated cards
            with open(FLASHCARD_FILE, "w") as file:
                json.dump(flashcards, file)

            # Reload the display
            self.load_cards()
            messagebox.showinfo("Success", "✅  Cards deleted successfully !")

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected or len(selected) > 1:
            messagebox.showinfo("Info", "Please select exactly one card to edit")
            return

        # Get the selected card data
        item = self.tree.item(selected[0])
        class_name, question, answer = item['values']

        # Create edit dialog
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Flashcard")
        edit_window.geometry("400x300")

        # Add edit fields
        ttk.Label(edit_window, text="Class:").pack(pady=5)
        class_entry = ttk.Entry(edit_window, width=40)
        class_entry.insert(0, class_name)
        class_entry.pack(pady=5)

        ttk.Label(edit_window, text="Question:").pack(pady=5)
        question_entry = ttk.Entry(edit_window, width=40)
        question_entry.insert(0, question)
        question_entry.pack(pady=5)

        ttk.Label(edit_window, text="Answer:").pack(pady=5)
        answer_entry = ttk.Entry(edit_window, width=40)
        answer_entry.insert(0, answer)
        answer_entry.pack(pady=5)

        def save_changes():
            # Load current cards
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)

            # Update the selected card
            index = int(selected[0])
            flashcards[index] = {
                "class_name": class_entry.get(),
                "question": question_entry.get(),
                "answer": answer_entry.get()
            }

            # Save updated cards
            with open(FLASHCARD_FILE, "w") as file:
                json.dump(flashcards, file)

            # Reload the display
            self.load_cards()
            edit_window.destroy()

        ttk.Button(
            edit_window,
            text="Save Changes",
            command=save_changes
        ).pack(pady=20)


class Card:
    def __init__(self, question, answer, class_name):
        self.question = question
        self.answer = answer
        self.class_name = class_name
        self.level = 0  # Proficiency level
        self.next_review = datetime.now()  # Next review date

    def update_level(self, correct):
        if correct:
            self.level += 1
            # Exponential spacing
            days = 2 ** self.level
            self.next_review = datetime.now() + timedelta(days=days)
        else:
            self.level = max(0, self.level - 1)
            self.next_review = datetime.now()


class Settings:
    def __init__(self):
        self.settings = {
            "font_size": 12,
            "cards_per_session": 20,
            "show_progress": True
        }
        self.load_settings()

    def load_settings(self):
        self.settings.update(safe_json_load("settings.json", {}))

    def save_settings(self, new_settings):
        try:
            with open("settings.json", "w") as f:
                json.dump(new_settings, f)
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False


class SettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("600x400")  # Increased settings window size

        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(expand=True)

        # Font size
        ttk.Label(main_frame, text="Font Size:").pack()
        self.font_scale = ttk.Scale(
            main_frame,
            from_=10,
            to=20,
            orient="horizontal"
        )
        self.font_scale.set(12)
        self.font_scale.pack(pady=(0, 20))

        # Cards per session
        ttk.Label(main_frame, text="Cards per Study Session:").pack()
        self.cards_scale = ttk.Scale(
            main_frame,
            from_=5,
            to=50,
            orient="horizontal"
        )
        self.cards_scale.set(20)
        self.cards_scale.pack(pady=(0, 20))

        # Show progress option
        self.show_progress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Show Progress Bar",
            variable=self.show_progress_var
        ).pack(pady=10)

        # Save button
        ttk.Button(
            main_frame,
            text="Save",
            command=self.save_settings
        ).pack(pady=20)

        self.load_existing_settings()

    def save_settings(self):
        settings = {
            "font_size": int(self.font_scale.get()),
            "cards_per_session": int(self.cards_scale.get()),
            "show_progress": self.show_progress_var.get()
        }

        with open("settings.json", "w") as f:
            json.dump(settings, f)

        messagebox.showinfo("Success", "Settings saved!")
        self.window.destroy()

    def load_existing_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.font_scale.set(settings.get("font_size", 12))
                self.cards_scale.set(settings.get("cards_per_session", 20))
                self.show_progress_var.set(settings.get("show_progress", True))


# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
