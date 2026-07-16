import customtkinter as ctk
from datetime import datetime
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY_BOLD, FONT_BODY, FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from utils.validators import is_valid_amount
from database.db_manager import (
    get_budget_status, set_budget, get_categories
)

class BudgetPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Grid settings
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header Row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(header_frame, text="Monthly Budgets", font=FONT_TITLE, text_color=COLOR_TEXT)
        title_label.pack(side="left")
        
        # Month selector dropdown
        self.month_var = ctk.StringVar(value=datetime.today().strftime("%Y-%m"))
        self.month_menu = ctk.CTkOptionMenu(
            header_frame,
            variable=self.month_var,
            font=FONT_BODY,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY,
            command=self.on_month_change
        )
        self.month_menu.pack(side="right")
        
        month_label = ctk.CTkLabel(
            header_frame, 
            text="Month: ", 
            font=FONT_BODY_BOLD, 
            text_color=COLOR_TEXT
        )
        month_label.pack(side="right", padx=10)
        
        # Tip banner
        tip_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS, height=45)
        tip_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        tip_lbl = ctk.CTkLabel(
            tip_frame, 
            text="💡 Tip: Set spending limits to track and control expenses. Progress bars color-code automatically.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED
        )
        tip_lbl.pack(pady=10, padx=20, anchor="w")
        
        # Budgets List (Scroll Frame)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, padx=30, pady=(10, 30), sticky="nsew")

    def on_show(self):
        """Lifecycle hook: refresh data."""
        self.load_month_list()
        self.load_budget_list()

    def load_month_list(self):
        """Pre-populates dropdown options around current date."""
        # Hardcode a range of +/- 6 months for simple user budgeting
        curr_year = datetime.today().year
        curr_month = datetime.today().month
        
        month_options = []
        # Prepopulate past 6 and next 6 months
        for i in range(-6, 7):
            m = curr_month + i
            y = curr_year
            while m <= 0:
                m += 12
                y -= 1
            while m > 12:
                m -= 12
                y += 1
            month_options.append(f"{y}-{m:02d}")
            
        # Unique and sorted list descending
        options = sorted(list(set(month_options)), reverse=True)
        self.month_menu.configure(values=options)

    def on_month_change(self, value):
        """Listens to dropdown value updates and triggers list reload."""
        self.load_budget_list()

    def load_budget_list(self):
        """Loads categories status and maps progress values."""
        user = self.controller.current_user
        if not user:
            return
            
        # Clean existing items
        for child in self.scroll_frame.winfo_children():
            child.destroy()
            
        month = self.month_var.get()
        budgets_status = get_budget_status(user.user_id, month)
        
        if not budgets_status:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="Please create expense categories first in the Categories tab.",
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            empty_lbl.pack(pady=40)
            return
            
        for idx, status in enumerate(budgets_status):
            # Row panel
            row_card = ctk.CTkFrame(
                self.scroll_frame, 
                fg_color=COLOR_CARD, 
                corner_radius=CORNER_RADIUS,
                border_width=1,
                border_color=("#E5E7EB", "#2D2D31")
            )
            row_card.pack(fill="x", pady=6, padx=2)
            
            # Row grids
            # Col 0: Text details (Category Name, Spent / Limit)
            # Col 1: Progress bar
            # Col 2: Action Button ("Set Budget")
            row_card.grid_columnconfigure(0, weight=2)
            row_card.grid_columnconfigure(1, weight=3)
            row_card.grid_columnconfigure(2, weight=1)
            
            # 1. Text Labels Frame
            info_frame = ctk.CTkFrame(row_card, fg_color="transparent")
            info_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")
            
            cat_name_lbl = ctk.CTkLabel(
                info_frame, 
                text=status["category_name"], 
                font=FONT_BODY_BOLD, 
                text_color=COLOR_TEXT
            )
            cat_name_lbl.pack(anchor="w")
            
            limit = status["limit_amount"]
            spent = status["spent"]
            
            if limit == 0:
                stats_text = f"Spent: ₹{spent:,.2f}  •  No Budget Set"
                stats_color = COLOR_TEXT_MUTED
            else:
                stats_text = f"Spent: ₹{spent:,.2f} of ₹{limit:,.2f}"
                stats_color = COLOR_DANGER if status["is_over"] else COLOR_TEXT
                
            stats_lbl = ctk.CTkLabel(
                info_frame, 
                text=stats_text, 
                font=FONT_SMALL, 
                text_color=stats_color
            )
            stats_lbl.pack(anchor="w", pady=(2, 0))
            
            # 2. Progress Bar
            progress_val = min(status["percent"], 1.0)
            
            # Decide color based on percentage
            if limit == 0:
                # Flat background bar if no limit set
                pb_color = COLOR_TEXT_MUTED
                progress_val = 0.0
            elif status["percent"] <= 0.7:
                pb_color = COLOR_SUCCESS
            elif status["percent"] <= 1.0:
                pb_color = COLOR_WARNING
            else:
                pb_color = COLOR_DANGER
                
            pb = ctk.CTkProgressBar(
                row_card,
                height=12,
                corner_radius=6,
                progress_color=pb_color[1] if isinstance(pb_color, tuple) else pb_color
            )
            pb.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
            pb.set(progress_val)
            
            # 3. Action button
            action_btn = ctk.CTkButton(
                row_card,
                text="Set Limit",
                font=FONT_BODY_BOLD,
                width=100,
                height=35,
                corner_radius=BUTTON_CORNER_RADIUS,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                command=lambda s=status: self.open_limit_dialog(s)
            )
            action_btn.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def open_limit_dialog(self, status):
        """Launches target popup modal to change category budget limit amount."""
        popup = ctk.CTkToplevel(self)
        popup.title("Configure Limit")
        popup.geometry("320x220")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()
        
        x = self.winfo_screenwidth() // 2 - 160
        y = self.winfo_screenheight() // 2 - 110
        popup.geometry(f"+{x}+{y}")
        
        lbl = ctk.CTkLabel(
            popup, 
            text=f"Set Budget Limit for '{status['category_name']}'\nMonth: {self.month_var.get()}", 
            font=FONT_BODY_BOLD, 
            text_color=COLOR_TEXT,
            justify="center",
            pady=15
        )
        lbl.pack()
        
        entry = ctk.CTkEntry(popup, font=FONT_BODY, width=220, placeholder_text="0.00")
        if status["limit_amount"] > 0:
            entry.insert(0, str(status["limit_amount"]))
        entry.pack(pady=5)
        
        status_lbl = ctk.CTkLabel(popup, text="", font=FONT_SMALL, text_color=COLOR_DANGER)
        status_lbl.pack()
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=15, fill="x", padx=30)
        
        def save_limit():
            limit_val = entry.get().strip()
            
            if not limit_val:
                status_lbl.configure(text="Please enter an amount.")
                return
                
            if not is_valid_amount(limit_val):
                status_lbl.configure(text="Please enter a valid amount (> 0).")
                return
                
            success = set_budget(
                user_id=self.controller.current_user.user_id,
                category_id=status["category_id"],
                month=self.month_var.get(),
                limit_amount=float(limit_val)
            )
            
            if success:
                popup.destroy()
                self.load_budget_list()
                # Update Dashboard alerts if initialized
                if "dashboard" in self.controller.frames:
                    self.controller.frames["dashboard"].on_show()
            else:
                status_lbl.configure(text="Failed to save budget. Try again.")
                
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
        cancel_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        save_btn = ctk.CTkButton(
            btn_frame, 
            text="Save Limit",
            font=FONT_BODY_BOLD,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=110,
            command=save_limit
        )
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")
