import tkinter as tk
from tkinter import ttk, messagebox
from .base import BaseWindow
from ..config import SETTINGS_WINDOW_SIZE
from ..services.ai_service import AICardGenerator
from ..utils import save_json, safe_json_load, FLASHCARD_FILE, get_available_classes

class LoadingAnimation:
    def __init__(self, window):
        self.window = window
        self.frame = ttk.Frame(window)
        self.frame.pack(pady=20)
        
        self.label = ttk.Label(
            self.frame,
            text="🤖 Generating cards",
            font=("Arial", 14)
        )
        self.label.pack()
        
        self.dots = ""
        self.is_running = False
        
    def start(self):
        self.is_running = True
        self.animate()
        
    def stop(self):
        self.is_running = False
        self.frame.destroy()
        
    def animate(self):
        if not self.is_running:
            return
            
        self.dots = self.dots + "." if len(self.dots) < 3 else ""
        self.label.config(text=f"🤖 Generating cards{self.dots}")
        
        # Différentes émojis pour l'animation
        emojis = ["🤖", "⚡", "✨", "🔮", "💫"]
        current_emoji = emojis[len(self.dots) % len(emojis)]
        self.label.config(text=f"{current_emoji} Generating cards{self.dots}")
        
        self.window.after(500, self.animate)

class GenerateCardsWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Generate Cards", SETTINGS_WINDOW_SIZE)
        self.setup_ui()

    def setup_ui(self):
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="🤖 AI Card Generator",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        # Topic/Prompt entry with scrollbar
        topic_frame = ttk.LabelFrame(
            main_frame, 
            text="Topic/Instructions (max 2000 characters)", 
            padding=10
        )
        topic_frame.pack(fill="x", padx=20, pady=10)

        # Add scrollbar to topic entry
        topic_scroll = ttk.Scrollbar(topic_frame)
        topic_scroll.pack(side="right", fill="y")

        # Use Text widget instead of Entry for larger input
        self.topic_text = tk.Text(
            topic_frame,
            height=5,  # Make it 5 lines tall
            width=50,
            wrap="word",  # Enable word wrapping
            yscrollcommand=topic_scroll.set,
            font=("Arial", 11)
        )
        self.topic_text.pack(fill="both", expand=True, pady=5)
        topic_scroll.config(command=self.topic_text.yview)

        # Add character counter
        self.char_count_label = ttk.Label(
            topic_frame,
            text="0/2000 characters"
        )
        self.char_count_label.pack(anchor="e", padx=5)

        # Bind character counting
        self.topic_text.bind('<KeyRelease>', self.update_char_count)

        # Class selection
        class_frame = ttk.LabelFrame(main_frame, text="Class", padding=10)
        class_frame.pack(fill="x", padx=20, pady=10)

        # Get existing classes
        classes = sorted(get_available_classes())
        self.class_var = tk.StringVar()
        
        # Radio buttons for class selection
        self.class_choice = tk.StringVar(value="existing")
        ttk.Radiobutton(
            class_frame,
            text="Use existing class",
            variable=self.class_choice,
            value="existing",
            command=self.toggle_class_input
        ).pack(anchor="w")

        self.class_combobox = ttk.Combobox(
            class_frame,
            values=classes,
            textvariable=self.class_var,
            width=40,
            font=("Arial", 11)
        )
        self.class_combobox.pack(pady=5)

        ttk.Radiobutton(
            class_frame,
            text="Create new class",
            variable=self.class_choice,
            value="new",
            command=self.toggle_class_input
        ).pack(anchor="w")

        self.new_class_entry = ttk.Entry(
            class_frame,
            width=40,
            font=("Arial", 11),
            state="disabled"
        )
        self.new_class_entry.pack(pady=5)

        # Number of cards
        num_frame = ttk.LabelFrame(main_frame, text="Number of Cards", padding=10)
        num_frame.pack(fill="x", padx=20, pady=10)

        self.num_cards = tk.IntVar(value=5)
        ttk.Scale(
            num_frame,
            from_=1,
            to=20,
            orient="horizontal",
            variable=self.num_cards,
            command=lambda _: self.update_num_label()
        ).pack(fill="x", padx=10)

        self.num_label = ttk.Label(num_frame, text="5 cards")
        self.num_label.pack()

        # Difficulty selection
        diff_frame = ttk.LabelFrame(main_frame, text="Difficulty", padding=10)
        diff_frame.pack(fill="x", padx=20, pady=10)

        self.difficulty = tk.StringVar(value="mixed")
        for diff in ["easy", "medium", "hard", "mixed"]:
            ttk.Radiobutton(
                diff_frame,
                text=diff.capitalize(),
                variable=self.difficulty,
                value=diff
            ).pack(side="left", padx=10)

        # Generate button
        ttk.Button(
            main_frame,
            text="🔮 Generate Cards",
            command=self.generate_cards,
            style="Action.TButton",
            width=25
        ).pack(pady=20)

        # Return button
        ttk.Button(
            main_frame,
            text="↩️ Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=25
        ).pack(pady=10)

    def toggle_class_input(self):
        if self.class_choice.get() == "existing":
            self.class_combobox.config(state="normal")
            self.new_class_entry.config(state="disabled")
        else:
            self.class_combobox.config(state="disabled")
            self.new_class_entry.config(state="normal")

    def update_num_label(self):
        self.num_label.config(text=f"{self.num_cards.get()} cards")

    def update_char_count(self, event=None):
        """Update character count label and enforce limit"""
        content = self.topic_text.get("1.0", "end-1c")
        count = len(content)
        self.char_count_label.config(text=f"{count}/2000 characters")
        
        if count > 2000:
            # Truncate to 2000 chars
            self.topic_text.delete("1.0", "end")
            self.topic_text.insert("1.0", content[:2000])

    def generate_cards(self):
        """Modified to handle duplicate detection with animation"""
        topic = self.topic_text.get("1.0", "end-1c").strip()
        if not topic:
            messagebox.showwarning("Input Error", "Please enter a topic!")
            return

        if len(topic) > 2000:
            messagebox.showwarning("Input Error", "Topic exceeds 2000 character limit!")
            return

        # Get class name
        if self.class_choice.get() == "existing":
            class_name = self.class_var.get()
            if not class_name:
                messagebox.showwarning("Input Error", "Please select a class!")
                return
        else:
            class_name = self.new_class_entry.get().strip()
            if not class_name:
                messagebox.showwarning("Input Error", "Please enter a new class name!")
                return

        # Show loading animation
        self.window.config(cursor="wait")
        loading = LoadingAnimation(self.window)
        loading.start()
        self.window.update()

        try:
            # Load existing cards
            existing_cards = safe_json_load(FLASHCARD_FILE, [])

            # Generate cards and check for duplicates
            new_cards, duplicate_count = AICardGenerator.generate_unique_cards(
                topic,
                self.num_cards.get(),
                self.difficulty.get(),
                existing_cards
            )

            if not new_cards:
                raise Exception("Failed to generate cards")

            # Add new cards
            for card in new_cards:
                card_dict = {
                    "question": card["question"],
                    "answer": card["answer"],
                    "class_name": class_name,
                    "difficulty": self.difficulty.get()
                }
                existing_cards.append(card_dict)

            # Save cards
            if save_json(FLASHCARD_FILE, existing_cards):
                message = f"✨ Generated {len(new_cards)} new flashcards for '{class_name}'!"
                if duplicate_count > 0:
                    message += f"\n\n{duplicate_count} similar cards were filtered out."
                
                messagebox.showinfo("Success", message)
                self.return_to_main()
            else:
                raise Exception("Failed to save cards")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate cards: {str(e)}")

        finally:
            # Stop animation
            loading.stop()
            self.window.config(cursor="")

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window) 