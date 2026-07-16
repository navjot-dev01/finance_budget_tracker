from database.db_manager import initialize_db
from gui.app import App

def main():
    # Initialize the database structures
    initialize_db()
    
    # Launch main customtkinter application
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()