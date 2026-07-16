import customtkinter as ctk
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")  # Ensure correct backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY_BOLD, FONT_BODY, FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from database.db_manager import get_transactions, get_categories, get_monthly_summary

class ReportsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Grid config: Row 0: Header, Row 1: Month Selector, Row 2: Charts container
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header Row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        
        title_label = ctk.CTkLabel(header_frame, text="Financial Reports", font=FONT_TITLE, text_color=COLOR_TEXT)
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
            text="Report Month: ", 
            font=FONT_BODY_BOLD, 
            text_color=COLOR_TEXT
        )
        month_label.pack(side="right", padx=10)
        
        # Charts Area (side-by-side)
        self.charts_container = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_container.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        self.charts_container.grid_rowconfigure(0, weight=1)
        self.charts_container.grid_columnconfigure((0, 1), weight=1, uniform="charts")
        
        # Left Panel: Expense Pie Chart
        self.pie_card = ctk.CTkFrame(self.charts_container, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.pie_card.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        self.pie_card.grid_columnconfigure(0, weight=1)
        self.pie_card.grid_rowconfigure(1, weight=1)
        
        pie_title = ctk.CTkLabel(self.pie_card, text="Category Expense Breakdown", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        pie_title.grid(row=0, column=0, pady=15)
        
        # Right Panel: 6-Month Trend Bar Chart
        self.bar_card = ctk.CTkFrame(self.charts_container, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.bar_card.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        self.bar_card.grid_columnconfigure(0, weight=1)
        self.bar_card.grid_rowconfigure(1, weight=1)
        
        bar_title = ctk.CTkLabel(self.bar_card, text="6-Month Income vs Expenses", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        bar_title.grid(row=0, column=0, pady=15)
        
        # Keep track of active canvas objects so we can destroy them on reload
        self.pie_canvas = None
        self.bar_canvas = None

    def on_show(self):
        """Lifecycle hook: refresh lists and regenerate charts."""
        self.load_month_list()
        self.generate_reports()

    def load_month_list(self):
        """Builds list of active transaction months."""
        user = self.controller.current_user
        if not user:
            return
            
        txs = get_transactions(user.user_id)
        months = set()
        for t in txs:
            try:
                dt = datetime.strptime(t.date, "%Y-%m-%d")
                months.add(dt.strftime("%Y-%m"))
            except ValueError:
                pass
                
        curr = datetime.today().strftime("%Y-%m")
        months.add(curr)
        
        sorted_months = sorted(list(months), reverse=True)
        self.month_menu.configure(values=sorted_months)
        
        if self.month_var.get() not in sorted_months:
            self.month_var.set(curr)

    def on_month_change(self, value):
        """Trigger update when selector value shifts."""
        self.generate_reports()

    def generate_reports(self):
        """Draws pie and bar charts mapped to application colors."""
        user = self.controller.current_user
        if not user:
            return
            
        month = self.month_var.get()
        
        # Determine theme styling for Matplotlib
        # customtkinter appearance returns "Dark" or "Light"
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        
        bg_hex = "#1E1E1E" if is_dark else "#FFFFFF"
        text_hex = "#F3F4F6" if is_dark else "#1F2937"
        
        # Clean existing canvases
        if self.pie_canvas:
            self.pie_canvas.get_tk_widget().destroy()
            self.pie_canvas = None
            
        if self.bar_canvas:
            self.bar_canvas.get_tk_widget().destroy()
            self.bar_canvas = None
            
        # Close all active pyplot figures to save memory
        plt.close('all')
        
        # 1. PIE CHART: Category Expense Breakdown
        transactions = get_transactions(user.user_id, t_type="expense", month=month)
        
        # Group amounts by category name
        expense_map = {}
        for t in transactions:
            expense_map[t.category_name] = expense_map.get(t.category_name, 0.0) + t.amount
            
        if not expense_map:
            # Fallback when empty
            lbl = ctk.CTkLabel(
                self.pie_card, 
                text="No expenses recorded for this month.", 
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            lbl.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
            self.pie_canvas = None
        else:
            # Remove any residual labels in row 1
            for child in self.pie_card.grid_slaves(row=1, column=0):
                if isinstance(child, ctk.CTkLabel):
                    child.destroy()
                    
            fig, ax = plt.subplots(figsize=(4, 4.5), facecolor=bg_hex)
            ax.set_facecolor(bg_hex)
            
            categories = list(expense_map.keys())
            amounts = list(expense_map.values())
            
            # Curated modern pastel palette
            colors = ["#6366F1", "#10B981", "#EF4444", "#FBBF24", "#3B82F6", "#EC4899", "#8B5CF6", "#14B8A6"]
            
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories, 
                autopct="%1.1f%%",
                startangle=140,
                colors=colors[:len(categories)],
                textprops=dict(color=text_hex, fontsize=9, fontweight="bold")
            )
            
            # Make sure percentages texts are high contrast
            for autotext in autotexts:
                autotext.set_color('white')
                
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            
            # Embed canvas
            self.pie_canvas = FigureCanvasTkAgg(fig, self.pie_card)
            self.pie_canvas.draw()
            self.pie_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
            
        # 2. BAR CHART: 6-Month Income vs Expenses
        # Calculate last 6 months chronologically
        curr_dt = datetime.strptime(month, "%Y-%m")
        months_list = []
        for i in range(5, -1, -1):
            m = curr_dt.month - i
            y = curr_dt.year
            while m <= 0:
                m += 12
                y -= 1
            months_list.append(f"{y}-{m:02d}")
            
        income_trends = []
        expense_trends = []
        
        for m in months_list:
            summary = get_monthly_summary(user.user_id, m)
            income_trends.append(summary["total_income"])
            expense_trends.append(summary["total_expense"])
            
        # Render Bar chart if there's any data
        if sum(income_trends) == 0 and sum(expense_trends) == 0:
            lbl = ctk.CTkLabel(
                self.bar_card, 
                text="No transaction history across the last 6 months.", 
                font=FONT_BODY,
                text_color=COLOR_TEXT_MUTED
            )
            lbl.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
            self.bar_canvas = None
        else:
            for child in self.bar_card.grid_slaves(row=1, column=0):
                if isinstance(child, ctk.CTkLabel):
                    child.destroy()
                    
            fig, ax = plt.subplots(figsize=(4, 4.5), facecolor=bg_hex)
            ax.set_facecolor(bg_hex)
            
            # Setup bar positions
            import numpy as np
            x = np.arange(len(months_list))
            width = 0.35
            
            # Translate labels for nicer view e.g. "2026-07" -> "Jul 26"
            month_labels = []
            for m in months_list:
                dt = datetime.strptime(m, "%Y-%m")
                month_labels.append(dt.strftime("%b %y"))
                
            ax.bar(x - width/2, income_trends, width, label='Income', color=COLOR_SUCCESS[0])
            ax.bar(x + width/2, expense_trends, width, label='Expense', color=COLOR_DANGER[0])
            
            ax.set_ylabel('Amount (₹)', color=text_hex, fontweight="bold")
            ax.set_xticks(x)
            ax.set_xticklabels(month_labels, color=text_hex, fontweight="bold", rotation=25)
            
            # Tick colors
            ax.tick_params(axis='y', colors=text_hex)
            ax.spines['bottom'].set_color(text_hex)
            ax.spines['left'].set_color(text_hex)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            ax.legend(facecolor=bg_hex, labelcolor=text_hex)
            ax.grid(axis='y', linestyle='--', alpha=0.3, color=text_hex)
            
            fig.tight_layout()
            
            # Embed canvas
            self.bar_canvas = FigureCanvasTkAgg(fig, self.bar_card)
            self.bar_canvas.draw()
            self.bar_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
