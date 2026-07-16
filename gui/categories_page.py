import customtkinter as ctk
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY,
    FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from database.db_manager import (
    get_categories, insert_category, edit_category, delete_category, category_has_transactions
)

class CategoriesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Main grid config: Col 0: Add Category Form (35%), Col 1: Tabbed Categories List (65%)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        
        # Header Row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=30, pady=(30, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(header_frame, text="Categories Settings", font=FONT_TITLE, text_color=COLOR_TEXT)
        title_label.pack(side="left")
        
        # 1. Left Frame: Add Category Card
        self.add_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.add_card.grid(row=1, column=0, padx=(30, 15), pady=(10, 30), sticky="nsew")
        
        self.add_card.grid_columnconfigure(0, weight=1)
        
        card_title = ctk.CTkLabel(self.add_card, text="Create New Category", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        card_title.pack(pady=(25, 20), padx=20, anchor="w")
        
        # Name Input
        name_label = ctk.CTkLabel(self.add_card, text="Category Name", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        name_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.name_input = ctk.CTkEntry(
            self.add_card,
            placeholder_text="e.g. Groceries, Gym, Stocks",
            font=FONT_BODY,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS
        )
        self.name_input.pack(pady=5, padx=20, fill="x")
        
        # Type Input
        type_label = ctk.CTkLabel(self.add_card, text="Category Type", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        type_label.pack(pady=(15, 5), padx=20, anchor="w")
        
        self.type_var = ctk.StringVar(value="expense")
        self.type_selector = ctk.CTkSegmentedButton(
            self.add_card,
            values=["income", "expense"],
            variable=self.type_var,
            font=FONT_BODY_BOLD,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            selected_color=COLOR_PRIMARY[1]
        )
        self.type_selector.pack(pady=5, padx=20, fill="x")
        
        # Status Message
        self.status_label = ctk.CTkLabel(self.add_card, text="", font=FONT_SMALL)
        self.status_label.pack(pady=(10, 5), padx=20)
        
        # Add Button
        self.add_btn = ctk.CTkButton(
            self.add_card,
            text="Add Category",
            font=FONT_BODY_BOLD,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.on_add_click
        )
        self.add_btn.pack(pady=(10, 25), padx=20, fill="x")
        
        # 2. Right Frame: Tab View Categories
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.grid(row=1, column=1, padx=(15, 30), pady=(10, 30), sticky="nsew")
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(
            self.list_frame,
            corner_radius=CORNER_RADIUS,
            fg_color=COLOR_CARD,
            segmented_button_selected_color=COLOR_PRIMARY[1],
            segmented_button_selected_hover_color=COLOR_PRIMARY_HOVER[1]
        )
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        self.tabview.add("Expense Categories")
        self.tabview.add("Income Categories")
        
        # Configure layout for tab views
        self.tabview.tab("Expense Categories").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Expense Categories").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Income Categories").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Income Categories").grid_columnconfigure(0, weight=1)
        
        # Scroll frames inside tabs
        self.expense_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Expense Categories"), fg_color="transparent")
        self.expense_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.income_scroll = ctk.CTkScrollableFrame(self.tabview.tab("Income Categories"), fg_color="transparent")
        self.income_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def on_show(self):
        """Lifecycle hook: refresh list."""
        self.load_categories_lists()
        self.status_label.configure(text="")
        self.name_input.delete(0, "end")

    def load_categories_lists(self):
        """Fetches categories and updates lists for both expense and income tabs."""
        user = self.controller.current_user
        if not user:
            return
            
        # Clear existing
        for child in self.expense_scroll.winfo_children():
            child.destroy()
        for child in self.income_scroll.winfo_children():
            child.destroy()
            
        # Load from DB
        expense_cats = get_categories(user.user_id, "expense")
        income_cats = get_categories(user.user_id, "income")
        
        # Populate Expense List
        if not expense_cats:
            lbl = ctk.CTkLabel(self.expense_scroll, text="No expense categories.", font=FONT_BODY, text_color=COLOR_TEXT_MUTED)
            lbl.pack(pady=20)
        else:
            for cat in expense_cats:
                self.create_cat_row(self.expense_scroll, cat)
                
        # Populate Income List
        if not income_cats:
            lbl = ctk.CTkLabel(self.income_scroll, text="No income categories.", font=FONT_BODY, text_color=COLOR_TEXT_MUTED)
            lbl.pack(pady=20)
        else:
            for cat in income_cats:
                self.create_cat_row(self.income_scroll, cat)

    def create_cat_row(self, scroll_parent, cat):
        """Creates a modern row widget inside a category scroll list."""
        row = ctk.CTkFrame(
            scroll_parent, 
            fg_color=("#F3F4F6", "#2D2D32"), 
            corner_radius=BUTTON_CORNER_RADIUS, 
            height=45
        )
        row.pack(fill="x", pady=2)
        row.grid_propagate(False)
        row.grid_rowconfigure(0, weight=1)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        
        # Name
        name_lbl = ctk.CTkLabel(row, text=cat.name, font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        name_lbl.grid(row=0, column=0, padx=15, sticky="w")
        
        # Action Buttons frame
        act_frame = ctk.CTkFrame(row, fg_color="transparent")
        act_frame.grid(row=0, column=1, padx=10, sticky="e")
        
        edit_btn = ctk.CTkButton(
            act_frame,
            text="✏️",
            font=FONT_BODY,
            width=28,
            height=28,
            corner_radius=5,
            fg_color="transparent",
            hover_color=COLOR_PRIMARY_HOVER,
            command=lambda c=cat: self.open_rename_dialog(c)
        )
        edit_btn.pack(side="left", padx=2)
        
        del_btn = ctk.CTkButton(
            act_frame,
            text="🗑️",
            font=FONT_BODY,
            width=28,
            height=28,
            corner_radius=5,
            fg_color="transparent",
            hover_color=("#FCA5A5", "#7F1D1D"),
            command=lambda c=cat: self.confirm_delete_cat(c)
        )
        del_btn.pack(side="left", padx=2)

    def on_add_click(self):
        """Inserts a category into database and resets the list layout."""
        user = self.controller.current_user
        if not user:
            return
            
        name = self.name_input.get().strip()
        t_type = self.type_var.get()
        
        if not name:
            self.status_label.configure(text_color=COLOR_DANGER, text="Please enter a name.")
            return
            
        cat_id = insert_category(user.user_id, name, t_type)
        
        if cat_id:
            self.status_label.configure(text_color=COLOR_SUCCESS, text="Category created successfully!")
            self.name_input.delete(0, "end")
            self.load_categories_lists()
            
            # Update Add Transaction category items if page initialized
            if "add_transaction" in self.controller.frames:
                self.controller.frames["add_transaction"].on_show()
        else:
            self.status_label.configure(text_color=COLOR_DANGER, text="Category name already exists.")

    def open_rename_dialog(self, cat):
        """Opens prompt modal to change the category name."""
        popup = ctk.CTkToplevel(self)
        popup.title("Rename Category")
        popup.geometry("320x200")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        
        x = self.winfo_screenwidth() // 2 - 160
        y = self.winfo_screenheight() // 2 - 100
        popup.geometry(f"+{x}+{y}")
        
        lbl = ctk.CTkLabel(popup, text=f"Rename Category: '{cat.name}'", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        lbl.pack(pady=(20, 10))
        
        name_entry = ctk.CTkEntry(popup, font=FONT_BODY, width=240)
        name_entry.insert(0, cat.name)
        name_entry.pack(pady=10)
        
        status_lbl = ctk.CTkLabel(popup, text="", font=FONT_SMALL, text_color=COLOR_DANGER)
        status_lbl.pack()
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=30)
        
        def save_rename():
            new_name = name_entry.get().strip()
            if not new_name:
                status_lbl.configure(text="Name cannot be empty.")
                return
            if edit_category(cat.category_id, new_name):
                popup.destroy()
                self.load_categories_lists()
                # Update Add Transaction
                if "add_transaction" in self.controller.frames:
                    self.controller.frames["add_transaction"].on_show()
            else:
                status_lbl.configure(text="Duplicate name exists.")
                
        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel",
            font=FONT_BODY_BOLD,
            fg_color=("#E5E7EB", "#374151"),
            text_color=COLOR_TEXT,
            hover_color=("#D1D5DB", "#4B5563"),
            width=110,
            command=popup.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(
            btn_frame, 
            text="Save",
            font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=110,
            command=save_rename
        )
        save_btn.pack(side="right", padx=5)

    def confirm_delete_cat(self, cat):
        """Performs safety checks for active transactions, warning user if blocked."""
        has_tx = category_has_transactions(cat.category_id)
        
        popup = ctk.CTkToplevel(self)
        popup.title("Delete Category")
        popup.geometry("340x220" if has_tx else "340x180")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        
        x = self.winfo_screenwidth() // 2 - 170
        y = self.winfo_screenheight() // 2 - 110
        popup.geometry(f"+{x}+{y}")
        
        if has_tx:
            # Blocked state warning
            msg_lbl = ctk.CTkLabel(
                popup, 
                text="⚠️ Action Blocked ⚠️\n\nThis category contains active transactions.\nTo delete it, you must first delete or reassign\nthose transactions in the Transactions list.", 
                font=FONT_BODY,
                text_color=COLOR_DANGER,
                pady=15
            )
            msg_lbl.pack()
            
            ok_btn = ctk.CTkButton(
                popup, 
                text="Close",
                font=FONT_BODY_BOLD,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                command=popup.destroy
            )
            ok_btn.pack(pady=15)
        else:
            # Confirmation request
            msg_lbl = ctk.CTkLabel(
                popup, 
                text=f"Delete Category: '{cat.name}'?\n\nThis action cannot be undone.", 
                font=FONT_BODY_BOLD,
                text_color=COLOR_TEXT,
                pady=20
            )
            msg_lbl.pack()
            
            btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
            btn_frame.pack(fill="x", padx=30, pady=10)
            
            def delete_confirmed():
                delete_category(cat.category_id)
                popup.destroy()
                self.load_categories_lists()
                # Update Add Transaction page dropdowns
                if "add_transaction" in self.controller.frames:
                    self.controller.frames["add_transaction"].on_show()
                
            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancel",
                font=FONT_BODY_BOLD,
                fg_color=("#E5E7EB", "#374151"),
                text_color=COLOR_TEXT,
                hover_color=("#D1D5DB", "#4B5563"),
                width=120,
                command=popup.destroy
            )
            cancel_btn.pack(side="left", padx=5)
            
            ok_btn = ctk.CTkButton(
                btn_frame,
                text="Delete",
                font=FONT_BODY_BOLD,
                fg_color=COLOR_DANGER,
                hover_color=COLOR_DANGER_HOVER,
                width=120,
                command=delete_confirmed
            )
            ok_btn.pack(side="right", padx=5)
