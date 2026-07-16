import os

# Database Configuration
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "finance_tracker.db")

# Theme Colors (Light Theme, Dark Theme)
COLOR_BG = ("#F0F9FF", "#121212")           # Light sky blue / Dark black-grey
COLOR_CARD = ("#FFFFFF", "#1E1E1E")         # White / Dark card surface
COLOR_SIDEBAR = ("#E0F2FE", "#181818")      # Light sky blue sidebar / Very dark sidebar
COLOR_TEXT = ("#1F2937", "#F3F4F6")         # Dark charcoal / Off-white
COLOR_TEXT_MUTED = ("#6B7280", "#9CA3AF")   # Muted gray text

# Accent Colors
COLOR_PRIMARY = ("#4F46E5", "#6366F1")      # Indigo primary
COLOR_SUCCESS = ("#10B981", "#34D399")      # Emerald for Income / Budgets ok
COLOR_WARNING = ("#F59E0B", "#FBBF24")      # Amber for warning limits
COLOR_DANGER = ("#EF4444", "#F87171")       # Rose for Expense / Over-budget
COLOR_BALANCE = ("#2563EB", "#60A5FA")      # Blue for Net Balance

# Hover colors (usually slightly lighter or darker than the core accent)
COLOR_PRIMARY_HOVER = ("#4338CA", "#4F46E5")
COLOR_SUCCESS_HOVER = ("#059669", "#059669")
COLOR_DANGER_HOVER = ("#DC2626", "#DC2626")

# Fonts
FONT_TITLE = ("Outfit", 24, "bold")
FONT_SUBTITLE = ("Outfit", 18, "bold")
FONT_BODY_BOLD = ("Outfit", 13, "bold")
FONT_BODY = ("Outfit", 13, "normal")
FONT_SMALL = ("Outfit", 11, "normal")

# Default Categories
DEFAULT_INCOME_CATEGORIES = ["Salary", "Pocket Money", "Tutoring", "Gifts", "Investments", "Other Income"]
DEFAULT_EXPENSE_CATEGORIES = ["Food", "Travel", "Rent", "Entertainment", "Bills", "Shopping", "Health", "Other Expense"]

# App styling defaults
CORNER_RADIUS = 12
BUTTON_CORNER_RADIUS = 8
