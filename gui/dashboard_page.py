import customtkinter as ctk
from datetime import datetime
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_BALANCE, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY_BOLD, FONT_BODY, FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from database.db_manager import (
    get_monthly_summary, get_transactions, get_budget_status
)

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Grid config: Row 0: Title & Month, Row 1: Summary Cards, Row 2: Recent List & Budget Warnings
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Row 0: Top Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        self.welcome_label = ctk.CTkLabel(
            header_frame, 
            text="Welcome back!", 
            font=FONT_TITLE, 
            text_color=COLOR_TEXT
        )
        self.welcome_label.pack(side="left")
        
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
            text="Selected Month: ", 
            font=FONT_BODY_BOLD, 
            text_color=COLOR_TEXT
        )
        month_label.pack(side="right", padx=10)
        
        # --- Row 1: Summary Cards Frame ---
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=30, pady=10)
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Card 1: Income
        self.inc_card = ctk.CTkFrame(self.cards_frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS, border_width=1.5, border_color=COLOR_SUCCESS[0])
        self.inc_card.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        self.setup_summary_card(self.inc_card, "📈 Total Income", "₹0.00", COLOR_SUCCESS)
        
        # Card 2: Expense
        self.exp_card = ctk.CTkFrame(self.cards_frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS, border_width=1.5, border_color=COLOR_DANGER[0])
        self.exp_card.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.setup_summary_card(self.exp_card, "📉 Total Expenses", "₹0.00", COLOR_DANGER)
        
        # Card 3: Balance
        self.bal_card = ctk.CTkFrame(self.cards_frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS, border_width=1.5, border_color=COLOR_BALANCE[0])
        self.bal_card.grid(row=0, column=2, padx=(10, 0), pady=5, sticky="nsew")
        self.setup_summary_card(self.bal_card, "💰 Net Balance", "₹0.00", COLOR_BALANCE)
        
        # --- Row 2: Bottom Details (Recent list & Alert banner) ---
        self.details_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=30, pady=15)
        self.details_frame.grid_rowconfigure(0, weight=1)
        self.details_frame.grid_columnconfigure(0, weight=6, uniform="det") # Left recent list
        self.details_frame.grid_columnconfigure(1, weight=4, uniform="det") # Right warnings
        
        # Left Details: Recent Transactions Card
        self.recent_card = ctk.CTkFrame(self.details_frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.recent_card.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        self.setup_recent_transactions_layout()
        
        # Right Details: Budget Alerts Card
        self.alert_card = ctk.CTkFrame(self.details_frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.alert_card.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        self.setup_alerts_layout()

    def on_show(self):
        """Lifecycle hook: updates user name, month lists, card statistics, recent items, and alerts."""
        user = self.controller.current_user
        if not user:
            return
            
        self.welcome_label.configure(text=f"Hello, {user.full_name}! 👋")
        self.load_month_list()
        self.load_dashboard_data()

    def load_month_list(self):
        """Loads unique months into selector from user transaction list."""
        user = self.controller.current_user
        txs = get_transactions(user.user_id)
        
        months = set()
        for t in txs:
            try:
                dt = datetime.strptime(t.date, "%Y-%m-%d")
                months.add(dt.strftime("%Y-%m"))
            except ValueError:
                pass
                
        # Add current month if empty
        curr = datetime.today().strftime("%Y-%m")
        months.add(curr)
        
        sorted_months = sorted(list(months), reverse=True)
        self.month_menu.configure(values=sorted_months)
        
        # Reset selection to current month if previous selected is no longer valid
        if self.month_var.get() not in sorted_months:
            self.month_var.set(curr)

    def on_month_change(self, value):
        """Handles month updates dynamically."""
        self.load_dashboard_data()

    def setup_summary_card(self, frame, label_text, amount_text, color_tuple):
        """Helper to create widgets inside a summary card frame."""
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure((0, 1), weight=1)
        
        lbl = ctk.CTkLabel(
            frame, 
            text=label_text, 
            font=FONT_BODY_BOLD, 
            text_color=COLOR_TEXT_MUTED
        )
        lbl.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Create text label with colors
        amt_lbl = ctk.CTkLabel(
            frame, 
            text=amount_text, 
            font=("Outfit", 26, "bold"), 
            text_color=color_tuple
        )
        amt_lbl.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Reference labels to change contents dynamically
        if "Income" in label_text:
            self.income_val_lbl = amt_lbl
        elif "Expenses" in label_text:
            self.expense_val_lbl = amt_lbl
        else:
            self.balance_val_lbl = amt_lbl

    def setup_recent_transactions_layout(self):
        """Creates skeletal layout for listing transactions."""
        self.recent_card.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            self.recent_card, 
            text="Recent Activity (Last 5)", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_TEXT
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Container for rows
        self.recent_rows_frame = ctk.CTkFrame(self.recent_card, fg_color="transparent")
        self.recent_rows_frame.pack(fill="both", expand=True, padx=15, pady=(0, 20))

    def setup_alerts_layout(self):
        """Creates budget alert section layout."""
        self.alert_card.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            self.alert_card, 
            text="Budget Alert Center", 
            font=FONT_SUBTITLE, 
            text_color=COLOR_TEXT
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.alert_scroll = ctk.CTkScrollableFrame(self.alert_card, fg_color="transparent")
        self.alert_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 20))

    def load_dashboard_data(self):
        """Queries SQLite and updates cards, activities list, and alert panel."""
        user = self.controller.current_user
        if not user:
            return
            
        month = self.month_var.get()
        
        # 1. Update Monthly summary cards
        summary = get_monthly_summary(user.user_id, month)
        self.income_val_lbl.configure(text=f"₹{summary['total_income']:,.2f}")
        self.expense_val_lbl.configure(text=f"₹{summary['total_expense']:,.2f}")
        
        bal = summary['balance']
        prefix = "+" if bal >= 0 else ""
        self.balance_val_lbl.configure(text=f"{prefix}₹{bal:,.2f}")
        
        # Color match balance card border & text
        if bal >= 0:
            self.bal_card.configure(border_color=COLOR_SUCCESS[0])
            self.balance_val_lbl.configure(text_color=COLOR_SUCCESS)
        else:
            self.bal_card.configure(border_color=COLOR_DANGER[0])
            self.balance_val_lbl.configure(text_color=COLOR_DANGER)
            
        # 2. Update Recent Activity List
        for child in self.recent_rows_frame.winfo_children():
            child.destroy()
            
        recent_txs = get_transactions(user_id=user.user_id, limit=5)
        
        if not recent_txs:
            lbl = ctk.CTkLabel(
                self.recent_rows_frame, 
                text="No transaction history yet.", 
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            lbl.pack(pady=40)
        else:
            for t in recent_txs:
                row = ctk.CTkFrame(
                    self.recent_rows_frame, 
                    fg_color=("#F3F4F6", "#2D2D32"), 
                    corner_radius=BUTTON_CORNER_RADIUS, 
                    height=45
                )
                row.pack(fill="x", pady=3)
                row.pack_propagate(False)
                
                # Details inside row
                t_color = COLOR_SUCCESS if t.type == "income" else COLOR_DANGER
                prefix = "+" if t.type == "income" else "-"
                
                # Text layout (Date | Category -> Amount)
                label_txt = f"{t.date}  •  {t.category_name}"
                lbl_left = ctk.CTkLabel(row, text=label_txt, font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
                lbl_left.pack(side="left", padx=15)
                
                note_txt = f"({t.note})" if t.note else ""
                lbl_note = ctk.CTkLabel(row, text=note_txt, font=FONT_SMALL, text_color=COLOR_TEXT_MUTED)
                lbl_note.pack(side="left", padx=5)
                
                lbl_right = ctk.CTkLabel(
                    row, 
                    text=f"{prefix}₹{t.amount:,.2f}", 
                    font=FONT_BODY_BOLD, 
                    text_color=t_color
                )
                lbl_right.pack(side="right", padx=15)
                
        # 3. Update Budget Warnings
        for child in self.alert_scroll.winfo_children():
            child.destroy()
            
        status = get_budget_status(user.user_id, month)
        over_budget_cats = [s for s in status if s["is_over"]]
        
        if not over_budget_cats:
            lbl = ctk.CTkLabel(
                self.alert_scroll, 
                text="🎉 All budgets on track!\nNo categories exceeded limit.", 
                font=FONT_BODY_BOLD,
                text_color=COLOR_SUCCESS,
                justify="center"
            )
            lbl.pack(pady=40)
        else:
            for s in over_budget_cats:
                diff = s["spent"] - s["limit_amount"]
                warning_card = ctk.CTkFrame(
                    self.alert_scroll, 
                    fg_color=("#FEE2E2", "#7F1D1D"), # Red backgrounds
                    corner_radius=BUTTON_CORNER_RADIUS,
                    border_width=1,
                    border_color=COLOR_DANGER[0]
                )
                warning_card.pack(fill="x", pady=4)
                
                warn_lbl = ctk.CTkLabel(
                    warning_card,
                    text=f"⚠️ Over-Budget in {s['category_name']}!\nLimit: ₹{s['limit_amount']:.2f} | Spent: ₹{s['spent']:.2f}\nExceeded by: ₹{diff:.2f}",
                    font=FONT_SMALL,
                    text_color=("#991B1B", "#FCA5A5"), # High-contrast red texts
                    justify="left",
                    padx=15,
                    pady=10
                )
                warn_lbl.pack(fill="x")
