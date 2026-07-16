import customtkinter as ctk
from utils.constants import COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_DANGER, COLOR_SUCCESS, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY, FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
from utils.security import hash_password
from utils.validators import is_not_empty
from database.db_manager import insert_user

class RegisterPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Configure layout grids (centered single column)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Center container Card (slightly taller than login)
        self.card = ctk.CTkFrame(
            self, 
            width=420, 
            height=540, 
            fg_color=COLOR_CARD, 
            corner_radius=CORNER_RADIUS
        )
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)
        
        # Grid inside card
        self.card.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)
        self.card.grid_columnconfigure(0, weight=1)
        
        # Title
        self.logo_label = ctk.CTkLabel(
            self.card, 
            text="✨ Join Nav Finance", 
            font=FONT_TITLE,
            text_color=COLOR_TEXT
        )
        self.logo_label.grid(row=0, column=0, pady=(25, 0), sticky="s")
        
        self.subtitle_label = ctk.CTkLabel(
            self.card, 
            text="Start tracking your budget and saving money today.", 
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 15), sticky="n")
        
        # Full Name Input
        self.fullname_input = ctk.CTkEntry(
            self.card,
            placeholder_text="Full Name",
            width=300,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=FONT_BODY
        )
        self.fullname_input.grid(row=2, column=0, pady=6, sticky="n")
        
        # Username Input
        self.username_input = ctk.CTkEntry(
            self.card,
            placeholder_text="Username",
            width=300,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=FONT_BODY
        )
        self.username_input.grid(row=3, column=0, pady=6, sticky="n")
        
        # Password Input
        self.password_input = ctk.CTkEntry(
            self.card,
            placeholder_text="Password",
            show="*",
            width=300,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=FONT_BODY
        )
        self.password_input.grid(row=4, column=0, pady=6, sticky="n")
        
        # Confirm Password Input
        self.confirm_password_input = ctk.CTkEntry(
            self.card,
            placeholder_text="Confirm Password",
            show="*",
            width=300,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            font=FONT_BODY
        )
        self.confirm_password_input.grid(row=5, column=0, pady=6, sticky="n")
        
        # Status message label (hidden by default)
        self.status_label = ctk.CTkLabel(
            self.card,
            text="",
            font=FONT_SMALL,
            text_color=COLOR_DANGER
        )
        self.status_label.grid(row=6, column=0, pady=(2, 2), sticky="n")
        
        # Register Button
        self.register_btn = ctk.CTkButton(
            self.card,
            text="Create Account",
            font=FONT_BODY_BOLD,
            width=300,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.on_register_click
        )
        self.register_btn.grid(row=7, column=0, pady=8, sticky="n")
        
        # Back to Login Link Button
        self.login_link = ctk.CTkButton(
            self.card,
            text="Already have an account? Sign In",
            font=FONT_SMALL,
            width=300,
            height=28,
            fg_color="transparent",
            text_color=COLOR_PRIMARY[1],  # Always readable indigo
            hover=False,
            command=lambda: self.controller.show_login()
        )
        self.login_link.grid(row=8, column=0, pady=(0, 20), sticky="n")

    def on_register_click(self):
        fullname = self.fullname_input.get()
        username = self.username_input.get()
        password = self.password_input.get()
        confirm = self.confirm_password_input.get()
        
        # Input Validations
        if not is_not_empty(fullname) or not is_not_empty(username) or not is_not_empty(password):
            self.status_label.configure(text_color=COLOR_DANGER, text="Please fill in all fields.")
            return
            
        if len(username.strip()) < 3:
            self.status_label.configure(text_color=COLOR_DANGER, text="Username must be at least 3 characters.")
            return
            
        if len(password) < 6:
            self.status_label.configure(text_color=COLOR_DANGER, text="Password must be at least 6 characters.")
            return
            
        if password != confirm:
            self.status_label.configure(text_color=COLOR_DANGER, text="Passwords do not match.")
            return
            
        # Hash password and insert user
        pwd_hash = hash_password(password)
        user_id = insert_user(fullname, username, pwd_hash)
        
        if user_id:
            # Show success message and redirect
            self.status_label.configure(text_color=COLOR_SUCCESS, text="Account created! Redirecting to login...")
            self.card.after(1500, lambda: self.controller.show_login())
        else:
            self.status_label.configure(text_color=COLOR_DANGER, text="Username already exists.")
