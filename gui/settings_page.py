import customtkinter as ctk
from utils.constants import (
    COLOR_BG, COLOR_CARD, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY,
    FONT_SMALL, CORNER_RADIUS, BUTTON_CORNER_RADIUS
)
from utils.security import hash_password, check_password
from database.db_manager import update_user_profile, update_user_password, verify_user

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG)
        self.controller = controller
        
        # Grid settings: Col 0: Profile & Theme (50%), Col 1: Password (50%)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="settings")
        
        # Header Row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=30, pady=(30, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(header_frame, text="User Settings", font=FONT_TITLE, text_color=COLOR_TEXT)
        title_label.pack(side="left")
        
        # Left Panel (Profile & Theme)
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=1, column=0, padx=(30, 15), pady=(10, 30), sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Right Panel (Security/Password)
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=1, column=1, padx=(15, 30), pady=(10, 30), sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # --- LEFT PANEL CARDS ---
        # Card 1: Profile Info
        self.profile_card = ctk.CTkFrame(self.left_panel, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.profile_card.pack(fill="x", pady=(0, 20))
        
        p_title = ctk.CTkLabel(self.profile_card, text="Edit Profile Details", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        p_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        fn_lbl = ctk.CTkLabel(self.profile_card, text="Full Name", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        fn_lbl.pack(anchor="w", padx=20, pady=(5, 2))
        self.fullname_input = ctk.CTkEntry(self.profile_card, font=FONT_BODY, height=38, corner_radius=BUTTON_CORNER_RADIUS)
        self.fullname_input.pack(fill="x", padx=20, pady=5)
        
        un_lbl = ctk.CTkLabel(self.profile_card, text="Username", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        un_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        self.username_input = ctk.CTkEntry(self.profile_card, font=FONT_BODY, height=38, corner_radius=BUTTON_CORNER_RADIUS)
        self.username_input.pack(fill="x", padx=20, pady=5)
        
        self.profile_status = ctk.CTkLabel(self.profile_card, text="", font=FONT_SMALL)
        self.profile_status.pack(pady=5)
        
        profile_save_btn = ctk.CTkButton(
            self.profile_card,
            text="Save Profile Changes",
            font=FONT_BODY_BOLD,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.save_profile
        )
        profile_save_btn.pack(fill="x", padx=20, pady=(5, 25))
        
        # Card 2: Appearance Config
        self.theme_card = ctk.CTkFrame(self.left_panel, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.theme_card.pack(fill="x")
        
        t_title = ctk.CTkLabel(self.theme_card, text="Theme Appearance", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        t_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        t_desc = ctk.CTkLabel(
            self.theme_card, 
            text="Choose between Light mode, Dark mode, or follow your System preferences.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=350
        )
        t_desc.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Theme segmented button selector
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_selector = ctk.CTkSegmentedButton(
            self.theme_card,
            values=["Light", "Dark", "System"],
            variable=self.theme_var,
            font=FONT_BODY_BOLD,
            height=38,
            corner_radius=BUTTON_CORNER_RADIUS,
            selected_color=COLOR_PRIMARY[1],
            selected_hover_color=COLOR_PRIMARY_HOVER[1],
            command=self.change_theme
        )
        self.theme_selector.pack(fill="x", padx=20, pady=(5, 25))
        
        # --- RIGHT PANEL CARDS ---
        # Card 1: Password Update
        self.pwd_card = ctk.CTkFrame(self.right_panel, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        self.pwd_card.pack(fill="both", expand=True)
        
        s_title = ctk.CTkLabel(self.pwd_card, text="Security & Password", font=FONT_SUBTITLE, text_color=COLOR_TEXT)
        s_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        cur_lbl = ctk.CTkLabel(self.pwd_card, text="Current Password", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        cur_lbl.pack(anchor="w", padx=20, pady=(5, 2))
        self.cur_pwd_input = ctk.CTkEntry(self.pwd_card, show="*", font=FONT_BODY, height=38, corner_radius=BUTTON_CORNER_RADIUS)
        self.cur_pwd_input.pack(fill="x", padx=20, pady=5)
        
        new_lbl = ctk.CTkLabel(self.pwd_card, text="New Password", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        new_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        self.new_pwd_input = ctk.CTkEntry(self.pwd_card, show="*", font=FONT_BODY, height=38, corner_radius=BUTTON_CORNER_RADIUS)
        self.new_pwd_input.pack(fill="x", padx=20, pady=5)
        
        conf_lbl = ctk.CTkLabel(self.pwd_card, text="Confirm New Password", font=FONT_BODY_BOLD, text_color=COLOR_TEXT)
        conf_lbl.pack(anchor="w", padx=20, pady=(10, 2))
        self.conf_pwd_input = ctk.CTkEntry(self.pwd_card, show="*", font=FONT_BODY, height=38, corner_radius=BUTTON_CORNER_RADIUS)
        self.conf_pwd_input.pack(fill="x", padx=20, pady=5)
        
        self.pwd_status = ctk.CTkLabel(self.pwd_card, text="", font=FONT_SMALL)
        self.pwd_status.pack(pady=5)
        
        pwd_save_btn = ctk.CTkButton(
            self.pwd_card,
            text="Change Password",
            font=FONT_BODY_BOLD,
            height=40,
            corner_radius=BUTTON_CORNER_RADIUS,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.save_password
        )
        pwd_save_btn.pack(fill="x", padx=20, pady=(5, 25))

    def on_show(self):
        """Lifecycle hook: pre-fills profile settings values from user state."""
        user = self.controller.current_user
        if not user:
            return
            
        self.fullname_input.delete(0, "end")
        self.fullname_input.insert(0, user.full_name)
        
        self.username_input.delete(0, "end")
        self.username_input.insert(0, user.username)
        
        # Clear fields
        self.cur_pwd_input.delete(0, "end")
        self.new_pwd_input.delete(0, "end")
        self.conf_pwd_input.delete(0, "end")
        
        self.profile_status.configure(text="")
        self.pwd_status.configure(text="")
        self.theme_var.set(ctk.get_appearance_mode())

    def save_profile(self):
        """Validates and pushes user name/username updates to SQLite."""
        user = self.controller.current_user
        if not user:
            return
            
        fullname = self.fullname_input.get().strip()
        username = self.username_input.get().strip().lower()
        
        if not fullname or not username:
            self.profile_status.configure(text_color=COLOR_DANGER, text="Please fill in all fields.")
            return
            
        if len(username) < 3:
            self.profile_status.configure(text_color=COLOR_DANGER, text="Username must be at least 3 characters.")
            return
            
        success = update_user_profile(user.user_id, fullname, username)
        
        if success:
            user.full_name = fullname
            user.username = username
            self.profile_status.configure(text_color=COLOR_SUCCESS, text="Profile updated successfully!")
            # Rebuild sidebar info
            self.controller.setup_main_app_layout()
            # Switch back to settings screen
            self.controller.switch_page("settings")
        else:
            self.profile_status.configure(text_color=COLOR_DANGER, text="Username already taken.")

    def save_password(self):
        """Validates current credentials and hashes the new password choice."""
        user = self.controller.current_user
        if not user:
            return
            
        current_pwd = self.cur_pwd_input.get()
        new_pwd = self.new_pwd_input.get()
        confirm_pwd = self.conf_pwd_input.get()
        
        if not current_pwd or not new_pwd or not confirm_pwd:
            self.pwd_status.configure(text_color=COLOR_DANGER, text="Please fill in all fields.")
            return
            
        if len(new_pwd) < 6:
            self.pwd_status.configure(text_color=COLOR_DANGER, text="New password must be at least 6 characters.")
            return
            
        if new_pwd != confirm_pwd:
            self.pwd_status.configure(text_color=COLOR_DANGER, text="New passwords do not match.")
            return
            
        # Verify current password
        verified = verify_user(user.username, current_pwd)
        if not verified:
            self.pwd_status.configure(text_color=COLOR_DANGER, text="Incorrect current password.")
            return
            
        # Hash and update in DB
        hashed = hash_password(new_pwd)
        success = update_user_password(user.user_id, hashed)
        
        if success:
            user.password_hash = hashed
            self.pwd_status.configure(text_color=COLOR_SUCCESS, text="Password updated successfully!")
            self.cur_pwd_input.delete(0, "end")
            self.new_pwd_input.delete(0, "end")
            self.conf_pwd_input.delete(0, "end")
        else:
            self.pwd_status.configure(text_color=COLOR_DANGER, text="Failed to update password. Try again.")

    def change_theme(self, value):
        """Callback listener to switch application light/dark/system colors."""
        ctk.set_appearance_mode(value)
