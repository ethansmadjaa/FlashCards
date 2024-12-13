import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
import json
import os
import markdown
from datetime import datetime, timedelta

# File to store flashcards
FLASHCARD_FILE = "flashcards.json"


class AddCardsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Add Flashcards")
        self.window.geometry("500x500")

        # Class selection/entry
        self.class_label = tk.Label(self.window, text="Class:", font=("Arial", 16))
        self.class_label.pack(pady=10)

        self.class_var = tk.StringVar()
        self.class_combobox = ttk.Combobox(
            self.window,
            textvariable=self.class_var,
            width=47
        )
        self.update_class_list()
        self.class_combobox.pack(pady=10)

        # Add new class button and entry
        self.new_class_frame = ttk.Frame(self.window)
        self.new_class_frame.pack(pady=5)

        self.new_class_entry = ttk.Entry(self.new_class_frame, width=30)
        self.new_class_entry.pack(side=tk.LEFT, padx=5)

        self.add_class_button = ttk.Button(
            self.new_class_frame,
            text="Add New Class",
            command=self.add_new_class
        )
        self.add_class_button.pack(side=tk.LEFT, padx=5)

        # UI Elements
        self.question_label = tk.Label(self.window, text="Question:", font=("Arial", 16))
        self.question_label.pack(pady=10)

        self.question_entry = scrolledtext.ScrolledText(self.window, width=50, height=5)
        self.question_entry.pack(pady=10)

        self.answer_label = tk.Label(self.window, text="Answer:", font=("Arial", 16))
        self.answer_label.pack(pady=10)

        self.answer_entry = scrolledtext.ScrolledText(self.window, width=50, height=5)
        self.answer_entry.pack(pady=10)

        self.add_button = tk.Button(self.window, text="Add Flashcard", command=self.add_flashcard)
        self.add_button.pack(pady=10)

        # Bind Return key to add_flashcard
        self.window.bind('<Return>', lambda e: self.add_flashcard())

    def update_class_list(self):
        classes = set()
        if os.path.exists(FLASHCARD_FILE):
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)
                for card in flashcards:
                    if "class_name" in card:
                        classes.add(card["class_name"])
        self.class_combobox['values'] = sorted(list(classes))

    def add_flashcard(self):
        question = self.question_entry.get("1.0", tk.END).strip()
        answer = self.answer_entry.get("1.0", tk.END).strip()
        class_name = self.class_var.get().strip()

        if not class_name:
            messagebox.showwarning("Input Error", "Please enter a class name.")
            return

        if question and answer:
            flashcards = []
            if os.path.exists(FLASHCARD_FILE):
                with open(FLASHCARD_FILE, "r") as file:
                    flashcards = json.load(file)

            flashcards.append({
                "question": question,
                "answer": answer,
                "class_name": class_name
            })

            with open(FLASHCARD_FILE, "w") as file:
                json.dump(flashcards, file)

            messagebox.showinfo("Success", "Flashcard added successfully!")
            self.update_class_list()
            self.question_entry.delete("1.0", tk.END)
            self.answer_entry.delete("1.0", tk.END)
            self.question_entry.focus()
        else:
            messagebox.showwarning("Input Error", "Please enter both a question and an answer.")

    def add_new_class(self):
        new_class = self.new_class_entry.get().strip()
        if new_class:
            current_values = list(self.class_combobox['values'])
            if new_class not in current_values:
                current_values.append(new_class)
                self.class_combobox['values'] = sorted(current_values)
                self.class_var.set(new_class)  # Set the combobox to the new class
                self.new_class_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Info", "This class already exists!")
        else:
            messagebox.showwarning("Input Error", "Please enter a class name.")


class StudyWindow:
    def __init__(self, parent, class_name=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Study Flashcards - {class_name if class_name else 'All Classes'}")
        self.window.geometry("800x600")

        # Initialize data
        self.class_name = class_name
        self.flashcards = []
        self.current_index = 0
        self.answer_showing = False
        self.seen_cards = set()
        self.correct_count = 0
        self.total_attempted = 0

        # Load flashcards first
        self.load_flashcards()

        if not self.flashcards:
            messagebox.showinfo("No Flashcards", "Please add some flashcards first!")
            self.window.destroy()
            return

        # Main container
        self.main_container = ttk.Frame(self.window, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Progress section
        self.progress_frame = ttk.Frame(self.main_container)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))

        # Add a container to center the progress bar and label
        self.progress_center_frame = ttk.Frame(self.progress_frame)
        self.progress_center_frame.pack(expand=True)

        self.progress_bar = ttk.Progressbar(
            self.progress_center_frame,
            length=300,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)

        self.progress_label = ttk.Label(
            self.progress_center_frame,
            text="0%"
        )
        self.progress_label.pack(side=tk.LEFT)

        # Card display
        self.display_label = tk.Label(
            self.main_container,
            text="",
            font=("Arial", 18),
            wraplength=600,
            justify=tk.CENTER,
            bg="white",
            relief="raised",
            padx=20,
            pady=20
        )
        self.display_label.pack(fill=tk.BOTH, expand=True, pady=20)

        # Control buttons
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.show_answer_button = ttk.Button(
            self.button_frame,
            text="Show Answer (Space)",
            command=self.toggle_answer
        )
        self.show_answer_button.pack(pady=10)

        # Study controls
        self.study_frame = ttk.Frame(self.main_container)
        self.study_frame.pack(pady=10)

        self.correct_button = ttk.Button(
            self.study_frame,
            text="Correct (↑)",
            command=self.mark_correct,
            style="Correct.TButton"
        )
        self.correct_button.pack(side=tk.LEFT, padx=5)

        self.wrong_button = ttk.Button(
            self.study_frame,
            text="Wrong (↓)",
            command=self.mark_wrong,
            style="Wrong.TButton"
        )
        self.wrong_button.pack(side=tk.LEFT, padx=5)

        # Stats display
        self.stats_label = tk.Label(
            self.main_container,
            text="",
            font=("Arial", 12)
        )
        self.stats_label.pack(pady=10)

        # Completion frame (initially hidden)
        self.completion_frame = ttk.Frame(self.main_container)
        self.final_stats_label = tk.Label(
            self.completion_frame,
            text="",
            font=("Arial", 16),
            wraplength=400
        )
        self.final_stats_label.pack(pady=20)

        self.restart_button = ttk.Button(
            self.completion_frame,
            text="Study Again",
            command=self.restart_study
        )
        self.restart_button.pack(pady=10)

        self.close_button = ttk.Button(
            self.completion_frame,
            text="Close",
            command=self.window.destroy
        )
        self.close_button.pack(pady=10)

        # Keyboard bindings
        self.window.bind('<Right>', lambda e: self.next_flashcard())
        self.window.bind('<space>', lambda e: self.toggle_answer())
        self.window.bind('<Up>', lambda e: self.mark_correct())
        self.window.bind('<Down>', lambda e: self.mark_wrong())

        # Show first card and update progress
        self.show_flashcard()
        self.update_progress()

    def update_progress(self):
        if self.flashcards:
            progress = (len(self.seen_cards) / len(self.flashcards)) * 100
            self.progress_bar['value'] = progress
            self.progress_label.config(text=f"{progress:.0f}%")

    def load_flashcards(self):
        if os.path.exists(FLASHCARD_FILE):
            with open(FLASHCARD_FILE, "r") as file:
                all_flashcards = json.load(file)
                if self.class_name:
                    self.flashcards = [
                        card for card in all_flashcards
                        if card.get("class_name") == self.class_name
                    ]
                else:
                    self.flashcards = all_flashcards

    def show_flashcard(self):
        if self.flashcards:
            flashcard = self.flashcards[self.current_index]
            card_count = f"Card {self.current_index + 1} of {len(self.flashcards)}"
            self.display_label.config(
                text=f"{card_count}\n\nQ: {flashcard['question']}"
            )
        else:
            self.display_label.config(text="No flashcards available.")

    def next_flashcard(self):
        if not self.flashcards:
            messagebox.showinfo("No Flashcards", "No flashcards to display.")
            return

        # Add current card to seen cards
        self.seen_cards.add(self.current_index)

        # Update progress bar
        self.update_progress()

        # Check if all cards have been seen
        if len(self.seen_cards) >= len(self.flashcards):
            self.show_completion_screen()
            return

        # Find the next unseen card
        for i in range(len(self.flashcards)):
            next_index = (self.current_index + i + 1) % len(self.flashcards)
            if next_index not in self.seen_cards:
                self.current_index = next_index
                self.answer_showing = False
                self.show_flashcard()
                return

        # If we get here, all cards have been seen
        self.show_completion_screen()

    def toggle_answer(self):
        if not self.flashcards:
            return

        flashcard = self.flashcards[self.current_index]
        if self.answer_showing:
            self.show_flashcard()  # This will show the question
        else:
            card_count = f"Card {self.current_index + 1} of {len(self.flashcards)}"
            self.display_label.config(
                text=f"{card_count}\n\nA: {flashcard['answer']}"
            )
        self.answer_showing = not self.answer_showing

    def mark_correct(self):
        if not self.flashcards:
            return
        self.correct_count += 1
        self.total_attempted += 1
        self.update_stats()
        self.next_flashcard()
        self.update_progress()

    def mark_wrong(self):
        if not self.flashcards:
            return
        self.total_attempted += 1
        self.update_stats()
        self.next_flashcard()
        self.update_progress()

    def update_stats(self):
        percentage = (self.correct_count / max(1, self.total_attempted)) * 100
        self.stats_label.config(text=f"Correct: {self.correct_count}/{self.total_attempted} ({percentage:.1f}%)")

    def show_completion_screen(self):
        # Hide study controls
        self.display_label.pack_forget()
        self.button_frame.pack_forget()
        self.study_frame.pack_forget()
        self.stats_label.pack_forget()

        # Show completion frame
        self.completion_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Calculate final stats
        percentage = (self.correct_count / max(1, self.total_attempted)) * 100
        grade = self.calculate_grade(percentage)

        completion_text = (
            f"🎉 Study Session Complete! 🎉\n\n"
            f"Cards Studied: {self.total_attempted}\n"
            f"Correct Answers: {self.correct_count}\n"
            f"Success Rate: {percentage:.1f}%\n"
            f"Grade: {grade}"
        )

        self.final_stats_label.config(text=completion_text)

    def calculate_grade(self, percentage):
        if percentage >= 90:
            return "A 🌟"
        elif percentage >= 80:
            return "B ⭐"
        elif percentage >= 70:
            return "C ✨"
        elif percentage >= 60:
            return "D 💫"
        else:
            return "F 📚"

    def restart_study(self):
        # Reset all study progress
        self.seen_cards.clear()
        self.correct_count = 0
        self.total_attempted = 0
        self.current_index = 0
        self.answer_showing = False

        # Hide completion frame
        self.completion_frame.pack_forget()

        # Show study controls
        self.display_label.pack(pady=20)
        self.button_frame.pack(pady=10)
        self.study_frame.pack(pady=10)
        self.stats_label.pack(pady=5)

        # Update stats and show first card
        self.update_stats()
        self.show_flashcard()

    def load_study_history(self):
        history_file = "study_history.json"
        if os.path.exists(history_file):
            with open(history_file, "r") as file:
                return json.load(file)
        return {}


class ClassSelectionWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Select Class to Study")
        self.window.geometry("400x400")

        # Title
        self.title_label = tk.Label(
            self.window,
            text="Select a Class",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=20)

        # Get available classes
        self.classes = self.get_available_classes()

        # Create buttons for each class
        for class_name in sorted(self.classes):
            btn = ttk.Button(
                self.window,
                text=class_name,
                command=lambda c=class_name: self.start_study(c),
                width=30
            )
            btn.pack(pady=5)

        # Add "All Classes" button
        ttk.Button(
            self.window,
            text="Study All Classes",
            command=lambda: self.start_study(None),
            width=30
        ).pack(pady=20)

    def get_available_classes(self):
        classes = set()
        if os.path.exists(FLASHCARD_FILE):
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)
                for card in flashcards:
                    if "class_name" in card:
                        classes.add(card["class_name"])
        return classes

    def start_study(self, class_name):
        self.window.destroy()
        StudyWindow(self.window.master, class_name)


class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard App")
        self.root.geometry("800x600")

        # Load settings first
        self.settings = Settings()
        self.apply_theme()

        # Rest of the init code...

    def apply_theme(self):
        self.style = ttk.Style()
        if self.settings.settings["theme"] == "dark":
            self.root.configure(bg="#2c2c2c")
            self.style.configure("TFrame", background="#2c2c2c")
            self.style.configure("TButton", background="#404040", foreground="white")
            self.style.configure("TLabel", background="#2c2c2c", foreground="white")
            self.style.configure("Treeview",
                                 background="#404040",
                                 fieldbackground="#404040",
                                 foreground="white"
                                 )
        else:
            self.root.configure(bg="white")
            self.style.configure("TFrame", background="white")
            self.style.configure("TButton", background="#f0f0f0", foreground="black")
            self.style.configure("TLabel", background="white", foreground="black")
            self.style.configure("Treeview",
                                 background="white",
                                 fieldbackground="white",
                                 foreground="black"
                                 )

        # Apply font size
        font_size = self.settings.settings["font_size"]
        self.style.configure("TButton", font=("Arial", font_size))
        self.style.configure("TLabel", font=("Arial", font_size))

    def play_sound(self, sound_type):
        if self.settings.settings["enable_sounds"]:
            if sound_type == "correct":
                # You can use system beep for now
                self.root.bell()
                # For better sounds, you'd need to install and use a sound library like pygame
                # self.correct_sound.play()
            elif sound_type == "wrong":
                self.root.bell()
                # self.wrong_sound.play()

    def open_add_cards(self):
        AddCardsWindow(self.root)

    def open_class_selection(self):
        ClassSelectionWindow(self.root)

    def open_manager(self):
        CardManagerWindow(self.root)

    def import_cards(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        if file_path:
            # Import logic here
            pass

    def export_cards(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        if file_path:
            # Export logic here
            pass

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

        # Add control buttons with icons
        ttk.Button(
            self.button_frame,
            text="����️ Delete Selected",
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

        # Load cards from file
        if os.path.exists(FLASHCARD_FILE):
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)
                for i, card in enumerate(flashcards):
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

    def search_cards(self):
        search_term = self.search_entry.get().lower()
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.tree.selection_add(item)
            else:
                self.tree.selection_remove(item)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a card to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected card(s)?"):
            # Load current cards
            with open(FLASHCARD_FILE, "r") as file:
                flashcards = json.load(file)

            # Get indices to delete
            indices = [int(i) for i in selected]
            # Remove cards in reverse order to maintain correct indices
            for index in sorted(indices, reverse=True):
                flashcards.pop(index)

            # Save updated cards
            with open(FLASHCARD_FILE, "w") as file:
                json.dump(flashcards, file)

            # Reload the display
            self.load_cards()

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
            "theme": "light",
            "font_size": 12,
            "cards_per_session": 20,
            "show_progress": True,
            "enable_sounds": True
        }
        self.load_settings()

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                self.settings.update(json.load(f))


class SettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x500")

        # Create settings UI
        ttk.Label(
            self.window,
            text="⚙️ Settings",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        # Theme selection
        ttk.Label(self.window, text="Theme:").pack(pady=5)
        self.theme_var = tk.StringVar(value="light")
        ttk.Radiobutton(self.window, text="Light", value="light", variable=self.theme_var).pack()
        ttk.Radiobutton(self.window, text="Dark", value="dark", variable=self.theme_var).pack()

        # Font size
        ttk.Label(self.window, text="Font Size:").pack(pady=5)
        self.font_scale = ttk.Scale(self.window, from_=10, to=20, orient="horizontal")
        self.font_scale.set(12)  # Default font size
        self.font_scale.pack(padx=20, pady=5)

        # Cards per session
        ttk.Label(self.window, text="Cards per Study Session:").pack(pady=5)
        self.cards_scale = ttk.Scale(self.window, from_=5, to=50, orient="horizontal")
        self.cards_scale.set(20)  # Default number of cards
        self.cards_scale.pack(padx=20, pady=5)

        # Checkboxes for other options
        self.show_progress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.window,
            text="Show Progress Bar",
            variable=self.show_progress_var
        ).pack(pady=5)

        self.enable_sounds_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.window,
            text="Enable Sounds",
            variable=self.enable_sounds_var
        ).pack(pady=5)

        # Save button
        ttk.Button(
            self.window,
            text="Save Changes",
            command=self.save_settings
        ).pack(pady=20)

        # Load existing settings
        self.load_existing_settings()

    def load_existing_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.theme_var.set(settings.get("theme", "light"))
                self.font_scale.set(settings.get("font_size", 12))
                self.cards_scale.set(settings.get("cards_per_session", 20))
                self.show_progress_var.set(settings.get("show_progress", True))
                self.enable_sounds_var.set(settings.get("enable_sounds", True))

    def save_settings(self):
        settings = {
            "theme": self.theme_var.get(),
            "font_size": int(self.font_scale.get()),  # Make sure it's an integer
            "cards_per_session": int(self.cards_scale.get()),
            "show_progress": self.show_progress_var.get(),
            "enable_sounds": self.enable_sounds_var.get()
        }

        with open("settings.json", "w") as f:
            json.dump(settings, f)

        # Update parent app settings
        self.window.master.settings.settings = settings
        self.window.master.apply_theme()  # Apply new theme

        messagebox.showinfo("Success", "Settings saved successfully!\nSome changes may require restart.")
        self.window.destroy()


# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
