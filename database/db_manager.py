import sqlite3

DB_NAME="database/finance_tracker.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    return conn
# FOREIGN KEY links A row in one table to a row in another

def initialize_db():
    conn=get_connection()
    cursor=conn.cursor

    #user table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT_CURRENT_TIMESTAMP
                )
            """)  

    #category table  
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories(
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name  TEXT NOT NULL,
                type TEXT CHECK(type IN('income','expense')) NOT NULL ,
                FOREIGN KEY(user_id) REFERENCES users(user_id) 
                )
        """)
    
    #transaction table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                type TEXT CHECK(type IN('income','expensive')) NOT NULL,
                note TEXT NULL,
                date TEXT NOT NULL, 
                FOREIGN KEY(user_id) REFERENCES user(user_id),
                FOREIGN KEY(category_id) REFERENCES categories(category_id)
                )
        """)

# budget table  
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions(
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                month NOT NULL,
                limit_amount NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )  
            """)
    conn.commit()
    conn.close()
    print("Tables created successfully")