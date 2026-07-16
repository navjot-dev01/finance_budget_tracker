import customtkinter as ctk
from datetime import date
from tkcalendar import Calendar
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY,
    FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from utils.validators import is_valid_amount, is_valid_date, is_not_empty
from database.db_manager import get_categories, insert_transaction

class AddTransactionPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Grid settings
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Top title frame
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        title_label = ctk.CTkLabel(title_frame, text="Add Transaction", font=FONT_TITLE, text_color=COLOR_TEXT)
        title_label.pack(side="left")
        
        # Main form card
        self.form_card = ctk.CTkFrame(
            self, 
            fg_color=COLOR_CARD, 
            corner_radius=CORNER_RADIUS
        )
        self.form_card.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Grid layout inside form card
        # Left margin spacing, Form columns, Right margin spacing
        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_columnconfigure(1, weight=2)
        self.form_card.grid_columnconfigure(2, weight=1)
        
        row = 0
        
        # Type selection row
        type_label = ctk.CTkLabel(self.form_card, text="Transaction Type", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        type_label.grid(row=row, column=0, padx=(30, 10), pady=(30, 15), sticky="w")
        
        self.type_var = ctk.StringVar(value="expense")
        self.type_selector = ctk.CTkSegmentedButton(
            self.form_card,
            values=["income", "expense"],
            command=self.on_type_change,
            variable=self.type_var,
            font=FONT_BODY_BOLD,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            selected_color=COLOR_PRIMARY[1],
            selected_hover_color=COLOR_PRIMARY_HOVER[1]
        )
        self.type_selector.grid(row=row, column=1, padx=10, pady=(30, 15), sticky="ew")
        row += 1
        
        # Amount row
        amount_label = ctk.CTkLabel(self.form_card, text="Amount (₹)", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        amount_label.grid(row=row, column=0, padx=(30, 10), pady=15, sticky="w")
        
        self.amount_input = ctk.CTkEntry(
            self.form_card,
            placeholder_text="0.00",
            font=FONT_BODY,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS
        )
        self.amount_input.grid(row=row, column=1, padx=10, pady=15, sticky="ew")
        row += 1
        
        # Category row
        category_label = ctk.CTkLabel(self.form_card, text="Category", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        category_label.grid(row=row, column=0, padx=(30, 10), pady=15, sticky="w")
        
        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(
            self.form_card,
            variable=self.category_var,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER
        )
        self.category_menu.grid(row=row, column=1, padx=10, pady=15, sticky="ew")
        row += 1
        
        # Date row
        date_label = ctk.CTkLabel(self.form_card, text="Date (YYYY-MM-DD)", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        date_label.grid(row=row, column=0, padx=(30, 10), pady=15, sticky="w")
        
        date_input_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        date_input_frame.grid(row=row, column=1, padx=10, pady=15, sticky="ew")
        date_input_frame.grid_columnconfigure(0, weight=1)
        date_input_frame.grid_columnconfigure(1, weight=0)
        
        self.date_input = ctk.CTkEntry(
            date_input_frame,
            font=FONT_BODY,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS
        )
        self.date_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.calendar_btn = ctk.CTkButton(
            date_input_frame,
            text="📅 Select",
            font=FONT_BODY_BOLD,
            width=80,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            command=self.open_calendar
        )
        self.calendar_btn.grid(row=0, column=1, sticky="e")
        row += 1
        
        # Notes row
        notes_label = ctk.CTkLabel(self.form_card, text="Note / Description", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        notes_label.grid(row=row, column=0, padx=(30, 10), pady=15, sticky="w")
        
        self.notes_input = ctk.CTkEntry(
            self.form_card,
            placeholder_text="Enter detail (e.g. Starbucks, Uber rides)",
            font=FONT_BODY,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS
        )
        self.notes_input.grid(row=row, column=1, padx=10, pady=15, sticky="ew")
        row += 1
        
        # Status/Notification row
        self.status_label = ctk.CTkLabel(self.form_card, text="", font=FONT_BODY_BOLD)
        self.status_label.grid(row=row, column=1, pady=10, sticky="ew")
        row += 1
        
        # Buttons row
        btn_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        btn_frame.grid(row=row, column=1, pady=(15, 30), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            font=FONT_BODY_BOLD,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=("#E5E7EB", "#374151"),
            text_color=COLOR_TEXT,
            hover_color=("#D1D5DB", "#4B5563"),
            command=self.clear_form
        )
        self.clear_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Transaction",
            font=FONT_BODY_BOLD,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.on_save_click
        )
        self.save_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Set default values
        self.categories_map = {}
        self.clear_form()

    def on_show(self):
        """Lifecycle hook when page becomes visible."""
        self.load_categories()

    def load_categories(self):
        """Loads categories dynamically for the current user and active transaction type."""
        user = self.controller.current_user
        if not user:
            return
            
        t_type = self.type_var.get()
        categories = get_categories(user.user_id, t_type)
        
        self.categories_map = {c.name: c.category_id for c in categories}
        cat_names = list(self.categories_map.keys())
        
        if cat_names:
            self.category_menu.configure(values=cat_names)
            # Default to first category
            self.category_var.set(cat_names[0])
        else:
            self.category_menu.configure(values=["No Categories Created"])
            self.category_var.set("No Categories Created")

    def on_type_change(self, value):
        """Dynamic toggle listener when Income/Expense is switched."""
        self.load_categories()

    def open_calendar(self):
        """Opens a top-level popup dialog with calendar widget."""
        popup = ctk.CTkToplevel(self)
        popup.title("Select Date")
        popup.geometry("300x320")
        popup.resizable(False, False)
        popup.transient(self)  # Keep on top
        popup.grab_set()       # Focus strictly on calendar
        
        # Place popup nicely relative to screen
        x = self.winfo_screenwidth() // 2 - 150
        y = self.winfo_screenheight() // 2 - 160
        popup.geometry(f"+{x}+{y}")
        
        cal = Calendar(
            popup, 
            selectmode="day", 
            date_pattern="yyyy-mm-dd"
        )
        cal.pack(pady=20, fill="both", expand=True, padx=20)
        
        def select_date():
            self.date_input.delete(0, "end")
            self.date_input.insert(0, cal.get_date())
            popup.destroy()
            
        select_btn = ctk.CTkButton(
            popup,
            text="Confirm",
            font=FONT_BODY_BOLD,
            corner_radius=BUTTON_CORNER_RADIUS,
            command=select_date
        )
        select_btn.pack(pady=(0, 20))

    def clear_form(self):
        """Resets amount, notes, and resets date to today."""
        self.amount_input.delete(0, "end")
        self.notes_input.delete(0, "end")
        
        # Reset date to today
        self.date_input.delete(0, "end")
        self.date_input.insert(0, date.today().strftime("%Y-%m-%d"))
        
        self.status_label.configure(text="")
        
        # Load active categories
        self.load_categories()

    def on_save_click(self):
        """Validates and saves the transaction record to SQLite."""
        user = self.controller.current_user
        if not user:
            return
            
        amount_str = self.amount_input.get()
        t_type = self.type_var.get()
        cat_name = self.category_var.get()
        date_str = self.date_input.get()
        note = self.notes_input.get()
        
        # Validation checks
        if not is_valid_amount(amount_str):
            self.status_label.configure(text_color=COLOR_DANGER, text="Please enter a valid amount (> 0).")
            return
            
        if not is_valid_date(date_str):
            self.status_label.configure(text_color=COLOR_DANGER, text="Please enter a valid date (YYYY-MM-DD).")
            return
            
        if cat_name == "No Categories Created" or not cat_name:
            self.status_label.configure(text_color=COLOR_DANGER, text="Please create/select a valid category.")
            return
            
        category_id = self.categories_map.get(cat_name)
        if not category_id:
            self.status_label.configure(text_color=COLOR_DANGER, text="Invalid category selected.")
            return
            
        amount = float(amount_str)
        
        # Save to DB
        tx_id = insert_transaction(
            user_id=user.user_id,
            category_id=category_id,
            amount=amount,
            t_type=t_type,
            note=note,
            date_str=date_str
        )
        
        if tx_id:
            self.status_label.configure(text_color=COLOR_SUCCESS, text="Transaction saved successfully!")
            # Clear input fields except date
            self.amount_input.delete(0, "end")
            self.notes_input.delete(0, "end")
        else:
            self.status_label.configure(text_color=COLOR_DANGER, text="Failed to save transaction. Try again.")
