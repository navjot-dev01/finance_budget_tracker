import customtkinter as ctk
from datetime import datetime
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY,
    FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from utils.validators import is_valid_amount, is_valid_date
from database.db_manager import (
    get_transactions, get_categories, delete_transaction, update_transaction
)

class TransactionsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Grid layout
        self.grid_rowconfigure(2, weight=1)  # Table list stretches
        self.grid_columnconfigure(0, weight=1)
        
        # Header Row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(header_frame, text="History & Transactions", font=FONT_TITLE, text_color=COLOR_TEXT)
        title_label.pack(side="left")
        
        # Filter Frame
        self.filter_card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS, height=70)
        self.filter_card.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.filter_card.grid_propagate(False)
        self.filter_card.grid_rowconfigure(0, weight=1)
        self.filter_card.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Filter 1: Type
        self.filter_type_var = ctk.StringVar(value="All Types")
        self.filter_type_menu = ctk.CTkOptionMenu(
            self.filter_card,
            values=["All Types", "income", "expense"],
            variable=self.filter_type_var,
            command=self.on_filter_change,
            font=FONT_BODY,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY
        )
        self.filter_type_menu.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        # Filter 2: Category
        self.filter_cat_var = ctk.StringVar(value="All Categories")
        self.filter_cat_menu = ctk.CTkOptionMenu(
            self.filter_card,
            values=["All Categories"],
            variable=self.filter_cat_var,
            command=self.on_filter_change,
            font=FONT_BODY,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY
        )
        self.filter_cat_menu.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        
        # Filter 3: Month
        self.filter_month_var = ctk.StringVar(value="All Months")
        # Prepopulate with past 6 months and a default
        self.filter_month_menu = ctk.CTkOptionMenu(
            self.filter_card,
            values=["All Months"],
            variable=self.filter_month_var,
            command=self.on_filter_change,
            font=FONT_BODY,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY
        )
        self.filter_month_menu.grid(row=0, column=2, padx=15, pady=15, sticky="ew")
        
        # Reset Filters Button
        self.reset_btn = ctk.CTkButton(
            self.filter_card,
            text="🔄 Reset Filters",
            font=FONT_BODY_BOLD,
            fg_color=("#E5E7EB", "#374151"),
            text_color=COLOR_TEXT,
            hover_color=("#D1D5DB", "#4B5563"),
            corner_radius=BUTTON_CORNER_RADIUS,
            command=self.reset_filters
        )
        self.reset_btn.grid(row=0, column=3, padx=15, pady=15, sticky="ew")
        
        # Transactions Table Area (Headers + Scrollable Frame)
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=2, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.table_container.grid_rowconfigure(1, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)
        
        # Table Headers
        self.headers_frame = ctk.CTkFrame(self.table_container, fg_color=COLOR_CARD, corner_radius=BUTTON_CORNER_RADIUS, height=40)
        self.headers_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.headers_frame.grid_propagate(False)
        self.headers_frame.grid_rowconfigure(0, weight=1)
        self.headers_frame.grid_columnconfigure(0, weight=3) # Date
        self.headers_frame.grid_columnconfigure(1, weight=3) # Category
        self.headers_frame.grid_columnconfigure(2, weight=2) # Type
        self.headers_frame.grid_columnconfigure(3, weight=3) # Amount
        self.headers_frame.grid_columnconfigure(4, weight=5) # Note
        self.headers_frame.grid_columnconfigure(5, weight=2) # Actions
        
        header_labels = ["Date", "Category", "Type", "Amount", "Note / Description", "Actions"]
        for idx, text in enumerate(header_labels):
            lbl = ctk.CTkLabel(
                self.headers_frame, 
                text=text, 
                font=FONT_BODY_BOLD, 
                text_color=COLOR_TEXT_MUTED
            )
            # Center type and actions, left-align rest
            sticky = "w" if idx not in [2, 5] else ""
            padx = 15 if sticky == "w" else 0
            lbl.grid(row=0, column=idx, padx=padx, sticky=sticky)
            
        # Scrollable rows frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container, 
            fg_color="transparent", 
            corner_radius=0
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        
        self.categories_map = {}

    def on_show(self):
        """Lifecycle hook: refresh data when selected."""
        self.load_filters()
        self.load_transaction_list()

    def load_filters(self):
        """Loads categories and months available in user transactions into the dropdown filters."""
        user = self.controller.current_user
        if not user:
            return
            
        # 1. Categories
        categories = get_categories(user.user_id)
        self.categories_map = {c.name: c.category_id for c in categories}
        cat_options = ["All Categories"] + list(self.categories_map.keys())
        self.filter_cat_menu.configure(values=cat_options)
        
        # 2. Months (dynamically extract all unique transaction months)
        txs = get_transactions(user.user_id)
        months = set()
        for t in txs:
            try:
                # date format: YYYY-MM-DD
                dt = datetime.strptime(t.date, "%Y-%m-%d")
                months.add(dt.strftime("%Y-%m"))
            except ValueError:
                pass
                
        sorted_months = sorted(list(months), reverse=True)
        month_options = ["All Months"] + sorted_months
        self.filter_month_menu.configure(values=month_options)

    def reset_filters(self):
        """Resets all active filters to defaults and reloads transactions."""
        self.filter_type_var.set("All Types")
        self.filter_cat_var.set("All Categories")
        self.filter_month_var.set("All Months")
        self.load_transaction_list()

    def on_filter_change(self, value):
        """Callback triggered when any filter selection option changes."""
        self.load_transaction_list()

    def load_transaction_list(self):
        """Queries database and renders list elements using customtkinter widgets."""
        user = self.controller.current_user
        if not user:
            return
            
        # Clear existing scroll rows
        for child in self.scroll_frame.winfo_children():
            child.destroy()
            
        # Extract filters
        t_type = self.filter_type_var.get()
        t_type_val = None if t_type == "All Types" else t_type
        
        cat_name = self.filter_cat_var.get()
        cat_id_val = self.categories_map.get(cat_name) if cat_name != "All Categories" else None
        
        month = self.filter_month_var.get()
        month_val = None if month == "All Months" else month
        
        transactions = get_transactions(
            user_id=user.user_id,
            category_id=cat_id_val,
            t_type=t_type_val,
            month=month_val
        )
        
        if not transactions:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame, 
                text="No transactions found matching the selected filters.", 
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return
            
        for idx, t in enumerate(transactions):
            row_bg = COLOR_CARD if idx % 2 == 0 else ("#F9FAFB", "#252529")
            
            row_frame = ctk.CTkFrame(
                self.scroll_frame, 
                fg_color=row_bg, 
                corner_radius=BUTTON_CORNER_RADIUS, 
                height=50
            )
            row_frame.pack(fill="x", pady=3)
            row_frame.grid_propagate(False)
            row_frame.grid_rowconfigure(0, weight=1)
            row_frame.grid_columnconfigure(0, weight=3) # Date
            row_frame.grid_columnconfigure(1, weight=3) # Category
            row_frame.grid_columnconfigure(2, weight=2) # Type
            row_frame.grid_columnconfigure(3, weight=3) # Amount
            row_frame.grid_columnconfigure(4, weight=5) # Note
            row_frame.grid_columnconfigure(5, weight=2) # Actions
            
            # 1. Date
            date_lbl = ctk.CTkLabel(row_frame, text=t.date, font=FONT_BODY, text_color=COLOR_TEXT)
            date_lbl.grid(row=0, column=0, padx=15, sticky="w")
            
            # 2. Category
            cat_lbl = ctk.CTkLabel(row_frame, text=t.category_name, font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
            cat_lbl.grid(row=0, column=1, padx=15, sticky="w")
            
            # 3. Type Pill
            type_text = t.type.upper()
            type_color = COLOR_SUCCESS if t.type == "income" else COLOR_DANGER
            
            type_lbl = ctk.CTkLabel(
                row_frame, 
                text=type_text, 
                font=FONT_SMALL, 
                text_color=type_color[1],
                fg_color=(type_color[0], "#2D3748"),
                corner_radius=4,
                width=75,
                height=22
            )
            type_lbl.grid(row=0, column=2, sticky="")
            
            # 4. Amount
            prefix = "+" if t.type == "income" else "-"
            amt_text = f"{prefix}₹{t.amount:,.2f}"
            amt_color = COLOR_SUCCESS if t.type == "income" else COLOR_DANGER
            
            amt_lbl = ctk.CTkLabel(row_frame, text=amt_text, font=FONT_BODY_BOLD, text_color=amt_color)
            amt_lbl.grid(row=0, column=3, padx=15, sticky="w")
            
            # 5. Note
            note_text = t.note if t.note else "-"
            note_lbl = ctk.CTkLabel(row_frame, text=note_text, font=FONT_BODY, text_color=COLOR_TEXT_MUTED, anchor="w", justify="left")
            note_lbl.grid(row=0, column=4, padx=15, sticky="w")
            
            # 6. Action buttons
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=5, sticky="")
            
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                font=FONT_BODY,
                width=30,
                height=30,
                corner_radius=6,
                fg_color="transparent",
                hover_color=COLOR_PRIMARY_HOVER,
                command=lambda tx=t: self.open_edit_dialog(tx)
            )
            edit_btn.pack(side="left", padx=2)
            
            del_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                font=FONT_BODY,
                width=30,
                height=30,
                corner_radius=6,
                fg_color="transparent",
                hover_color=("#FCA5A5", "#7F1D1D"),
                command=lambda tx=t: self.confirm_delete(tx)
            )
            del_btn.pack(side="left", padx=2)

    def confirm_delete(self, tx):
        """Displays a clean themed modal pop up asking user for confirmation."""
        popup = ctk.CTkToplevel(self)
        popup.title("Delete Transaction")
        popup.geometry("340x180")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        
        # Position popup center screen
        x = self.winfo_screenwidth() // 2 - 170
        y = self.winfo_screenheight() // 2 - 90
        popup.geometry(f"+{x}+{y}")
        
        msg_lbl = ctk.CTkLabel(
            popup, 
            text="Are you sure you want to delete\nthis transaction?", 
            font=FONT_BODY_BOLD,
            text_color=COLOR_TEXT,
            pady=20
        )
        msg_lbl.pack()
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=10)
        
        def delete_confirmed():
            delete_transaction(tx.transaction_id)
            popup.destroy()
            self.load_transaction_list()
            # Also refresh dashboard if it exists
            if "dashboard" in self.controller.frames:
                self.controller.frames["dashboard"].on_show()
            
        no_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=FONT_BODY_BOLD,
            fg_color=("#E5E7EB", "#374151"),
            text_color=COLOR_TEXT,
            hover_color=("#D1D5DB", "#4B5563"),
            width=120,
            command=popup.destroy
        )
        no_btn.pack(side="left", padx=5)
        
        yes_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            font=FONT_BODY_BOLD,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            width=120,
            command=delete_confirmed
        )
        yes_btn.pack(side="right", padx=5)

    def open_edit_dialog(self, tx):
        """Opens popup dialog with prefilled fields to edit transaction values."""
        popup = ctk.CTkToplevel(self)
        popup.title("Edit Transaction")
        popup.geometry("400x480")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        
        x = self.winfo_screenwidth() // 2 - 200
        y = self.winfo_screenheight() // 2 - 240
        popup.geometry(f"+{x}+{y}")
        
        # Layout components
        popup.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_columnconfigure(1, weight=2)
        
        # Title
        title = ctk.CTkLabel(popup, text="Edit Transaction Details", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Type
        type_lbl = ctk.CTkLabel(popup, text="Type", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        type_lbl.grid(row=1, column=0, padx=20, sticky="w")
        type_var = ctk.StringVar(value=tx.type)
        type_selector = ctk.CTkSegmentedButton(
            popup, 
            values=["income", "expense"],
            variable=type_var,
            font=FONT_BODY_BOLD,
            selected_color=COLOR_PRIMARY[1]
        )
        type_selector.grid(row=1, column=1, padx=20, sticky="ew")
        
        # Amount
        amt_lbl = ctk.CTkLabel(popup, text="Amount (₹)", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        amt_lbl.grid(row=2, column=0, padx=20, sticky="w")
        amt_input = ctk.CTkEntry(popup, font=FONT_BODY)
        amt_input.insert(0, str(tx.amount))
        amt_input.grid(row=2, column=1, padx=20, sticky="ew")
        
        # Categories list lookup
        cats = get_categories(self.controller.current_user.user_id, tx.type)
        cat_map = {c.name: c.category_id for c in cats}
        
        # Category Dropdown
        cat_lbl = ctk.CTkLabel(popup, text="Category", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        cat_lbl.grid(row=3, column=0, padx=20, sticky="w")
        cat_var = ctk.StringVar(value=tx.category_name)
        cat_menu = ctk.CTkOptionMenu(
            popup, 
            values=list(cat_map.keys()), 
            variable=cat_var,
            font=FONT_BODY,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY
        )
        cat_menu.grid(row=3, column=1, padx=20, sticky="ew")
        
        # Dynamic Category loading when Type changes
        def update_cats(val):
            new_cats = get_categories(self.controller.current_user.user_id, val)
            nonlocal cat_map
            cat_map = {c.name: c.category_id for c in new_cats}
            cat_list = list(cat_map.keys())
            cat_menu.configure(values=cat_list)
            if cat_list:
                cat_var.set(cat_list[0])
            else:
                cat_var.set("")
                
        type_selector.configure(command=update_cats)
        
        # Date
        date_lbl = ctk.CTkLabel(popup, text="Date (YYYY-MM-DD)", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        date_lbl.grid(row=4, column=0, padx=20, sticky="w")
        date_input = ctk.CTkEntry(popup, font=FONT_BODY)
        date_input.insert(0, tx.date)
        date_input.grid(row=4, column=1, padx=20, sticky="ew")
        
        # Note
        note_lbl = ctk.CTkLabel(popup, text="Note", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        note_lbl.grid(row=5, column=0, padx=20, sticky="w")
        note_input = ctk.CTkEntry(popup, font=FONT_BODY)
        note_input.insert(0, tx.note or "")
        note_input.grid(row=5, column=1, padx=20, sticky="ew")
        
        # Status
        status_lbl = ctk.CTkLabel(popup, text="", font=FONT_SMALL)
        status_lbl.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        def save_changes():
            amount_s = amt_input.get()
            date_s = date_input.get()
            typ_s = type_var.get()
            cat_s = cat_var.get()
            not_s = note_input.get()
            
            if not is_valid_amount(amount_s):
                status_lbl.configure(text_color=COLOR_DANGER, text="Please enter valid amount (> 0).")
                return
                
            if not is_valid_date(date_s):
                status_lbl.configure(text_color=COLOR_DANGER, text="Please enter valid date (YYYY-MM-DD).")
                return
                
            c_id = cat_map.get(cat_s)
            if not c_id:
                status_lbl.configure(text_color=COLOR_DANGER, text="Please select a valid category.")
                return
                
            success = update_transaction(
                transaction_id=tx.transaction_id,
                category_id=c_id,
                amount=float(amount_s),
                t_type=typ_s,
                note=not_s,
                date_str=date_s
            )
            
            if success:
                popup.destroy()
                self.load_transaction_list()
                if "dashboard" in self.controller.frames:
                    self.controller.frames["dashboard"].on_show()
            else:
                status_lbl.configure(text_color=COLOR_DANGER, text="Failed to save updates. Try again.")
                
        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel",
            font=FONT_BODY_BOLD,
            fg_color=("#E5E7EB", "#374151"),
            text_color=COLOR_TEXT,
            hover_color=("#D1D5DB", "#4B5563"),
            command=popup.destroy
        )
        cancel_btn.grid(row=0, column=0, padx=15, sticky="ew")
        
        save_btn = ctk.CTkButton(
            btn_frame, 
            text="Save Changes",
            font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=save_changes
        )
        save_btn.grid(row=0, column=1, padx=15, sticky="ew")
