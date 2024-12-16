import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from .base import BaseWindow
from ..config import ADD_CARDS_WINDOW_SIZE
from ..models import Card
from ..utils import save_json, safe_json_load, FLASHCARD_FILE, get_available_classes


class AddCardsWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Add Cards", ADD_CARDS_WINDOW_SIZE)

        # Initialize instance attributes
        self.class_var = tk.StringVar()
        self.class_combobox = None
        self.new_class_entry = None
        self.question_entry = None
        self.answer_entry = None

        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        """Set up the main UI components"""
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="✨ Add New Flashcard ✨",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))

        # Class selection frame
        self.setup_class_selection(main_frame)

        # Question frame
        question_frame = ttk.LabelFrame(main_frame, text="Question", padding=10)
        question_frame.pack(fill="x", padx=20, pady=10)

        self.question_entry = scrolledtext.ScrolledText(
            question_frame,
            width=50,
            height=5,
            font=("Arial", 11),
            wrap="word"
        )
        self.question_entry.pack(expand=True, fill="both")

        # Answer frame
        answer_frame = ttk.LabelFrame(main_frame, text="Answer", padding=10)
        answer_frame.pack(fill="x", padx=20, pady=10)

        self.answer_entry = scrolledtext.ScrolledText(
            answer_frame,
            width=50,
            height=5,
            font=("Arial", 11),
            wrap="word"
        )
        self.answer_entry.pack(expand=True, fill="both")

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="💾 Save Flashcard",
            command=self.save_flashcard,
            style="Action.TButton",
            width=25
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="↩️ Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=25
        ).pack(side="left", padx=10)

    def setup_class_selection(self, frame):
        """Set up the class selection combobox and new class entry"""
        class_frame = ttk.LabelFrame(frame, text="Class Selection", padding=10)
        class_frame.pack(fill="x", padx=20, pady=10)

        # Existing class selection
        selection_frame = ttk.Frame(class_frame)
        selection_frame.pack(fill="x", pady=5)

        ttk.Label(
            selection_frame,
            text="Select Existing Class:",
            font=("Arial", 11)
        ).pack(side="left", padx=5)

        self.class_combobox = ttk.Combobox(
            selection_frame,
            textvariable=self.class_var,
            width=30,
            font=("Arial", 11)
        )
        self.update_class_list()
        self.class_combobox.pack(side="left", padx=5)

        # New class entry
        new_class_frame = ttk.Frame(class_frame)
        new_class_frame.pack(fill="x", pady=5)

        ttk.Label(
            new_class_frame,
            text="Or Add New Class:",
            font=("Arial", 11)
        ).pack(side="left", padx=5)

        self.new_class_entry = ttk.Entry(
            new_class_frame,
            width=30,
            font=("Arial", 11)
        )
        self.new_class_entry.pack(side="left", padx=5)

        ttk.Button(
            new_class_frame,
            text="➕ Add Class",
            command=self.add_new_class,
            style="Action.TButton",
            width=15
        ).pack(side="left", padx=5)

    def update_class_list(self):
        """Update the class combobox with available classes"""
        classes = sorted(get_available_classes())
        self.class_combobox['values'] = classes
        if classes:
            self.class_combobox.set(classes[0])

    def add_new_class(self):
        """Add a new class to the list"""
        new_class = self.new_class_entry.get().strip()
        if not new_class:
            messagebox.showwarning("Input Error", "Please enter a class name!")
            return

        current_classes = set(self.class_combobox['values'])
        if new_class in current_classes:
            messagebox.showinfo("Info", "This class already exists!")
            return

        current_classes.add(new_class)
        self.class_combobox['values'] = sorted(current_classes)
        self.class_combobox.set(new_class)
        self.new_class_entry.delete(0, "end")

    def save_flashcard(self):
        """Save the flashcard to the JSON file"""
        question = self.question_entry.get("1.0", "end-1c").strip()
        answer = self.answer_entry.get("1.0", "end-1c").strip()
        class_name = self.class_var.get().strip()

        if not all([question, answer, class_name]):
            messagebox.showwarning(
                "Input Error",
                "Please fill in all fields (class, question, and answer)!"
            )
            return

        # Create new card
        card = Card(question, answer, class_name)

        # Load existing cards
        cards = safe_json_load(FLASHCARD_FILE, [])

        # Add new card
        cards.append(card.to_dict())

        # Save updated cards
        if save_json(FLASHCARD_FILE, cards):
            messagebox.showinfo(
                "Success",
                "✅ Flashcard added successfully!"
            )
            # Clear entries
            self.question_entry.delete("1.0", "end")
            self.answer_entry.delete("1.0", "end")
            self.question_entry.focus()
        else:
            messagebox.showerror(
                "Error",
                "Failed to save the flashcard. Please try again."
            )

    def return_to_main(self):
        """Return to the main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp  # Import here to avoid circular import
        FlashcardApp(self.window)


class CardManagerWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Manage Cards", ADD_CARDS_WINDOW_SIZE)

        # Initialize instance attributes
        self.tree = None
        self.search_entry = None
        self.class_filter = None
        self.class_var = tk.StringVar()

        self.setup_ui()
        self.load_cards()
        self.center_window()

    def setup_ui(self):
        """Set up the main UI components"""
        main_frame = self.create_main_frame()

        # Title
        ttk.Label(
            main_frame,
            text="📝 Manage Flashcards",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 20))

        # Search and filter frame
        self.setup_search_frame(main_frame)

        # Cards treeview
        self.setup_treeview(main_frame)

        # Action buttons
        self.setup_action_buttons(main_frame)

    def setup_search_frame(self, parent):
        """Set up search and filter controls"""
        search_frame = ttk.LabelFrame(parent, text="Search & Filter", padding=10)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Class filter
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(
            filter_frame,
            text="Filter by Class:",
            font=("Arial", 11)
        ).pack(side="left", padx=5)

        self.class_filter = ttk.Combobox(
            filter_frame,
            textvariable=self.class_var,
            width=30,
            font=("Arial", 11)
        )
        self.class_filter.pack(side="left", padx=5)

        # Search
        search_frame2 = ttk.Frame(search_frame)
        search_frame2.pack(fill="x", pady=5)

        ttk.Label(
            search_frame2,
            text="Search Cards:",
            font=("Arial", 11)
        ).pack(side="left", padx=5)

        self.search_entry = ttk.Entry(
            search_frame2,
            width=40,
            font=("Arial", 11)
        )
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(
            search_frame2,
            text="🔍 Search",
            command=self.apply_filters,
            style="Action.TButton",
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            search_frame2,
            text="❌ Clear",
            command=self.clear_filters,
            style="Action.TButton",
            width=15
        ).pack(side="left", padx=5)

    def setup_treeview(self, parent):
        """Set up the treeview for displaying cards"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Create treeview with scrollbars
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Class", "Question", "Answer"),
            show="headings",
            selectmode="browse"
        )

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Column headings
        self.tree.heading("Class", text="Class", command=lambda: self.sort_column("Class"))
        self.tree.heading("Question", text="Question", command=lambda: self.sort_column("Question"))
        self.tree.heading("Answer", text="Answer", command=lambda: self.sort_column("Answer"))

        # Column widths
        self.tree.column("Class", width=150, minwidth=100)
        self.tree.column("Question", width=300, minwidth=200)
        self.tree.column("Answer", width=300, minwidth=200)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

    def setup_action_buttons(self, parent):
        """Set up action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="✏️ Edit Selected",
            command=self.edit_selected,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            command=self.delete_selected,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

        # Add new button for checking duplicates
        ttk.Button(
            button_frame,
            text="🔍 Check Duplicates",
            command=self.check_duplicates,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="↩️ Return to Main Menu",
            command=self.return_to_main,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

    def load_cards(self):
        """Load cards into the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load cards
        cards = safe_json_load(FLASHCARD_FILE, [])
        
        # Insert cards with new indices
        for i, card in enumerate(cards):
            self.tree.insert(
                "",
                "end",
                values=(
                    card.get("class_name", ""),
                    card.get("question", ""),
                    card.get("answer", "")
                ),
                iid=str(i)
            )

        # Update class filter
        self.update_class_filter()

    def update_class_filter(self):
        """Update class filter combobox values"""
        classes = {"All Classes"}
        for item in self.tree.get_children():
            class_name = self.tree.item(item)["values"][0]
            if class_name:
                classes.add(class_name)
        self.class_filter["values"] = sorted(list(classes))
        self.class_filter.set("All Classes")

    def apply_filters(self):
        """Apply class and search filters"""
        selected_class = self.class_var.get()
        search_term = self.search_entry.get().lower()

        # First, clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load all cards
        cards = safe_json_load(FLASHCARD_FILE, [])

        # Insert only matching cards
        for i, card in enumerate(cards):
            # Check class match
            class_match = (selected_class == "All Classes" or 
                          card.get("class_name", "") == selected_class)
            
            # Check search match in all fields
            search_match = (
                not search_term or  # If no search term, consider it a match
                search_term in card.get("class_name", "").lower() or
                search_term in card.get("question", "").lower() or
                search_term in card.get("answer", "").lower()
            )

            # Insert if both conditions match
            if class_match and search_match:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        card.get("class_name", ""),
                        card.get("question", ""),
                        card.get("answer", "")
                    ),
                    iid=str(i)
                )

    def clear_filters(self):
        """Clear all filters and show all cards"""
        self.class_var.set("All Classes")
        self.search_entry.delete(0, tk.END)
        self.load_cards()  # Reload all cards

    def sort_column(self, col):
        """Sort treeview by column"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        items.sort()

        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

    def edit_selected(self):
        """Edit selected card"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a card to edit")
            return

        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Flashcard")
        edit_window.geometry("600x500")
        edit_window.transient(self.window)  # Make it modal
        edit_window.grab_set()  # Make it modal

        # Get selected card data
        item = self.tree.item(selected[0])
        class_name, question, answer = item["values"]

        # Create edit form
        ttk.Label(edit_window, text="Class:", font=("Arial", 11)).pack(pady=(20, 5))
        
        # Create combobox for class selection
        class_var = tk.StringVar(value=class_name)
        class_combobox = ttk.Combobox(
            edit_window,
            textvariable=class_var,
            width=40,
            font=("Arial", 11),
            state="readonly"  # Make it readonly to prevent typos
        )
        
        # Get available classes
        available_classes = sorted(get_available_classes())
        if class_name not in available_classes:
            available_classes.append(class_name)
        class_combobox['values'] = sorted(available_classes)
        
        class_combobox.pack(pady=(0, 10))

        ttk.Label(edit_window, text="Question:", font=("Arial", 11)).pack(pady=(10, 5))
        question_text = scrolledtext.ScrolledText(
            edit_window, width=50, height=5, font=("Arial", 11)
        )
        question_text.insert("1.0", question)
        question_text.pack(pady=(0, 10))

        ttk.Label(edit_window, text="Answer:", font=("Arial", 11)).pack(pady=(10, 5))
        answer_text = scrolledtext.ScrolledText(
            edit_window, width=50, height=5, font=("Arial", 11)
        )
        answer_text.insert("1.0", answer)
        answer_text.pack(pady=(0, 20))

        def save_changes():
            # Get updated values
            new_class = class_var.get()
            new_question = question_text.get("1.0", "end-1c").strip()
            new_answer = answer_text.get("1.0", "end-1c").strip()

            if not all([new_class, new_question, new_answer]):
                messagebox.showwarning(
                    "Input Error",
                    "Please fill in all fields!"
                )
                return

            # Update card in file
            cards = safe_json_load(FLASHCARD_FILE, [])
            index = int(selected[0])
            cards[index].update({
                "class_name": new_class,
                "question": new_question,
                "answer": new_answer
            })

            if save_json(FLASHCARD_FILE, cards):
                messagebox.showinfo("Success", "Card updated successfully!")
                edit_window.destroy()  # Only destroy the edit window
                self.load_cards()  # Refresh the card list
            else:
                messagebox.showerror("Error", "Failed to save changes")

        # Button frame
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=10)

        # Save button
        ttk.Button(
            button_frame,
            text="💾 Save Changes",
            command=save_changes,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

        # Cancel button
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=edit_window.destroy,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

    def delete_selected(self):
        """Delete selected card"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a card to delete")
            return

        if messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this card?"
        ):
            # Save current filter state
            current_class = self.class_var.get()
            current_search = self.search_entry.get()

            # Delete from file
            cards = safe_json_load(FLASHCARD_FILE, [])
            index = int(selected[0])
            cards.pop(index)

            if save_json(FLASHCARD_FILE, cards):
                messagebox.showinfo("Success", "Card deleted successfully!")
                
                # Clear and reload cards
                for item in self.tree.get_children():
                    self.tree.delete(item)
                    
                # Reload cards with new indices
                for i, card in enumerate(cards):
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            card.get("class_name", ""),
                            card.get("question", ""),
                            card.get("answer", "")
                        ),
                        iid=str(i)
                    )
                
                # Restore filter state
                self.class_var.set(current_class)
                self.search_entry.insert(0, current_search)
                
                # Reapply filters if they were active
                if current_class != "All Classes" or current_search:
                    self.apply_filters()
            else:
                messagebox.showerror("Error", "Failed to delete card")

    def return_to_main(self):
        """Return to main menu"""
        for widget in self.window.winfo_children():
            widget.destroy()
        from .app import FlashcardApp
        FlashcardApp(self.window)

    def manage_classes(self):
        """Open window to manage class names"""
        manage_window = tk.Toplevel(self.window)
        manage_window.title("Manage Classes")
        manage_window.geometry("500x400")
        manage_window.transient(self.window)
        manage_window.grab_set()

        # Get current classes
        classes = sorted(get_available_classes())

        # Create listbox for classes
        ttk.Label(
            manage_window,
            text="Select class to rename:",
            font=("Arial", 12)
        ).pack(pady=10)

        class_listbox = tk.Listbox(
            manage_window,
            width=40,
            height=10,
            font=("Arial", 11)
        )
        class_listbox.pack(pady=10, padx=20)

        # Populate listbox
        for class_name in classes:
            class_listbox.insert(tk.END, class_name)

        # New name entry
        ttk.Label(
            manage_window,
            text="New class name:",
            font=("Arial", 12)
        ).pack(pady=5)

        new_name_entry = ttk.Entry(
            manage_window,
            width=40,
            font=("Arial", 11)
        )
        new_name_entry.pack(pady=5)

        def rename_class():
            selection = class_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a class to rename")
                return

            old_name = class_listbox.get(selection[0])
            new_name = new_name_entry.get().strip()

            if not new_name:
                messagebox.showwarning("Warning", "Please enter a new class name")
                return

            if new_name in classes and new_name != old_name:
                messagebox.showwarning("Warning", "This class name already exists")
                return

            # Update all cards with this class name
            cards = safe_json_load(FLASHCARD_FILE, [])
            changes_made = False

            for card in cards:
                if card.get("class_name") == old_name:
                    card["class_name"] = new_name
                    changes_made = True

            if changes_made:
                if save_json(FLASHCARD_FILE, cards):
                    messagebox.showinfo("Success", f"Renamed class '{old_name}' to '{new_name}'")
                    manage_window.destroy()
                    self.load_cards()  # Refresh the card list
                else:
                    messagebox.showerror("Error", "Failed to save changes")
            else:
                messagebox.showinfo("Info", "No cards found with this class name")

        # Button frame
        button_frame = ttk.Frame(manage_window)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="✅ Rename Class",
            command=rename_class,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=manage_window.destroy,
            style="Action.TButton",
            width=20
        ).pack(side="left", padx=5)

    def check_duplicates(self):
        """Check for duplicate or similar cards"""
        cards = safe_json_load(FLASHCARD_FILE, [])
        if not cards:
            messagebox.showinfo("Info", "No cards to check")
            return

        # Create a window to show duplicates
        dup_window = tk.Toplevel(self.window)
        dup_window.title("Duplicate Cards")
        dup_window.geometry("1000x700")
        dup_window.transient(self.window)

        # Create main frame with padding
        main_frame = ttk.Frame(dup_window, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Add header
        ttk.Label(
            main_frame,
            text="🔍 Duplicate Cards Checker",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # Create scrolled text widget
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)

        # Add duplicate pairs list
        duplicates_frame = ttk.Frame(text_frame)
        duplicates_frame.pack(fill="both", expand=True, pady=10)

        # Create canvas for scrolling
        canvas = tk.Canvas(duplicates_frame)
        scrollbar = ttk.Scrollbar(duplicates_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Check for duplicates
        from ..services.ai_service import AICardGenerator
        duplicates_found = []

        # Group cards by class
        class_cards = {}
        for i, card in enumerate(cards):
            class_name = card.get('class_name', 'Unknown')
            if class_name not in class_cards:
                class_cards[class_name] = []
            class_cards[class_name].append((i, card))  # Store index with card

        # Check duplicates within each class
        for class_name, class_card_list in class_cards.items():
            for i, (idx1, card1) in enumerate(class_card_list):
                for idx2, card2 in class_card_list[i+1:]:
                    q1 = card1['question'].lower().strip()
                    q2 = card2['question'].lower().strip()
                    a1 = card1['answer'].lower().strip()
                    a2 = card2['answer'].lower().strip()
                    
                    question_similarity = AICardGenerator.check_similarity(q1, q2)
                    answer_similarity = AICardGenerator.check_similarity(a1, a2)

                    if question_similarity > 0.7 or answer_similarity > 0.7:
                        duplicates_found.append({
                            'class': class_name,
                            'card1': {'index': idx1, 'card': card1},
                            'card2': {'index': idx2, 'card': card2},
                            'q_sim': question_similarity,
                            'a_sim': answer_similarity
                        })

        if not duplicates_found:
            ttk.Label(
                scrollable_frame,
                text="No duplicate cards found!",
                font=("Arial", 12)
            ).pack(pady=20)
        else:
            # Show each duplicate pair
            for i, dup in enumerate(duplicates_found, 1):
                pair_frame = ttk.LabelFrame(
                    scrollable_frame,
                    text=f"Potential Duplicate Pair {i} (Class: {dup['class']})",
                    padding=10
                )
                pair_frame.pack(fill="x", pady=10, padx=5)

                # Card 1
                ttk.Label(
                    pair_frame,
                    text="Card 1:",
                    font=("Arial", 11, "bold")
                ).pack(anchor="w")
                ttk.Label(
                    pair_frame,
                    text=f"Q: {dup['card1']['card']['question']}",
                    wraplength=800
                ).pack(anchor="w")
                ttk.Label(
                    pair_frame,
                    text=f"A: {dup['card1']['card']['answer']}",
                    wraplength=800
                ).pack(anchor="w")

                # Card 2
                ttk.Label(
                    pair_frame,
                    text="Card 2:",
                    font=("Arial", 11, "bold")
                ).pack(anchor="w", pady=(10, 0))
                ttk.Label(
                    pair_frame,
                    text=f"Q: {dup['card2']['card']['question']}",
                    wraplength=800
                ).pack(anchor="w")
                ttk.Label(
                    pair_frame,
                    text=f"A: {dup['card2']['card']['answer']}",
                    wraplength=800
                ).pack(anchor="w")

                # Similarity info
                ttk.Label(
                    pair_frame,
                    text=f"Similarity - Question: {dup['q_sim']:.2f}, Answer: {dup['a_sim']:.2f}",
                    font=("Arial", 10, "italic")
                ).pack(pady=(5, 10))

                # Action buttons
                btn_frame = ttk.Frame(pair_frame)
                btn_frame.pack(fill="x")

                def create_keep_command(dup_info, keep_idx):
                    def command():
                        self.handle_duplicate(dup_info, keep_idx)
                    return command

                ttk.Button(
                    btn_frame,
                    text="Keep Card 1",
                    command=create_keep_command(dup, 1),
                    width=15
                ).pack(side="left", padx=5)

                ttk.Button(
                    btn_frame,
                    text="Keep Card 2",
                    command=create_keep_command(dup, 2),
                    width=15
                ).pack(side="left", padx=5)

                ttk.Button(
                    btn_frame,
                    text="Keep Both",
                    command=create_keep_command(dup, 0),
                    width=15
                ).pack(side="left", padx=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add close button at bottom
        ttk.Button(
            main_frame,
            text="Close",
            command=dup_window.destroy,
            style="Action.TButton",
            width=20
        ).pack(pady=10)

    def handle_duplicate(self, dup_info, keep_card):
        """Handle duplicate card resolution"""
        cards = safe_json_load(FLASHCARD_FILE, [])
        
        # Find the duplicate window
        dup_window = None
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.title() == "Duplicate Cards":
                dup_window = widget
                break

        if not dup_window:
            return

        # Handle the action
        if keep_card == 0:  # Keep both
            if messagebox.askyesno("Confirm", "Keep both cards?"):
                # No need to modify cards, but refresh displays
                messagebox.showinfo("Info", "Keeping both cards")
                # Destroy and recreate the duplicates window to refresh it
                dup_window.destroy()
                self.check_duplicates()
        else:
            # Determine which card to remove
            remove_idx = dup_info['card2']['index'] if keep_card == 1 else dup_info['card1']['index']
            
            # Remove the card
            if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected card?"):
                cards.pop(remove_idx)
                if save_json(FLASHCARD_FILE, cards):
                    messagebox.showinfo("Success", "Card deleted successfully!")
                    self.load_cards()  # Refresh the main window display
                    # Destroy and recreate the duplicates window to refresh it
                    dup_window.destroy()
                    self.check_duplicates()
                else:
                    messagebox.showerror("Error", "Failed to delete card")
