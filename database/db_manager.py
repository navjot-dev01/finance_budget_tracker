import sqlite3
import os
from utils.constants import DB_PATH, DEFAULT_INCOME_CATEGORIES, DEFAULT_EXPENSE_CATEGORIES
from models.user import User
from models.transaction import Transaction
from models.category import Category
from models.budget import Budget
from utils.security import check_password

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    # Ensure database directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def initialize_db():
    """Initializes the database and creates the required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # User table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        UNIQUE(user_id, name, type)
    )
    """)

    # Transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
        note TEXT,
        date TEXT NOT NULL, -- Format YYYY-MM-DD
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )
    """)

    # Budgets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        month TEXT NOT NULL, -- Format YYYY-MM
        limit_amount REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE,
        UNIQUE(user_id, category_id, month)
    )
    """)

    conn.commit()
    conn.close()

# --- User Functions ---

def insert_user(full_name, username, password_hash):
    """Inserts a new user into the database and auto-creates default categories."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (full_name, username, password_hash) VALUES (?, ?, ?)",
            (full_name.strip(), username.strip().lower(), password_hash)
        )
        user_id = cursor.lastrowid
        
        # Create default categories for user
        for cat in DEFAULT_INCOME_CATEGORIES:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (user_id, name, type) VALUES (?, ?, ?)",
                (user_id, cat, "income")
            )
        for cat in DEFAULT_EXPENSE_CATEGORIES:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (user_id, name, type) VALUES (?, ?, ?)",
                (user_id, cat, "expense")
            )
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Username already exists
    finally:
        conn.close()

def verify_user(username, password):
    """Verifies user credentials. Returns User object if verified, else None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password(password, row["password_hash"]):
        return User(
            user_id=row["user_id"],
            full_name=row["full_name"],
            username=row["username"],
            password_hash=row["password_hash"],
            created_at=row["created_at"]
        )
    return None

def update_user_profile(user_id, full_name, username):
    """Updates user's full name and/or username."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET full_name = ?, username = ? WHERE user_id = ?",
            (full_name.strip(), username.strip().lower(), user_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username taken
    finally:
        conn.close()

def update_user_password(user_id, new_password_hash):
    """Updates user's password."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# --- Category Functions ---

def insert_category(user_id, name, cat_type):
    """Inserts a new custom category."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
            (user_id, name.strip(), cat_type)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Duplicate name for this user
    finally:
        conn.close()

def get_categories(user_id, cat_type=None):
    """Fetches all categories for a user, optionally filtering by type."""
    conn = get_connection()
    cursor = conn.cursor()
    if cat_type:
        cursor.execute(
            "SELECT * FROM categories WHERE user_id = ? AND type = ? ORDER BY name ASC",
            (user_id, cat_type)
        )
    else:
        cursor.execute(
            "SELECT * FROM categories WHERE user_id = ? ORDER BY type DESC, name ASC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [Category(r["category_id"], r["user_id"], r["name"], r["type"]) for r in rows]

def edit_category(category_id, name):
    """Updates category name."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE categories SET name = ? WHERE category_id = ?",
            (name.strip(), category_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_category(category_id):
    """Deletes a category from the database. Only call if no transactions exist for it."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if any transactions are using this category
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
        if cursor.fetchone()[0] > 0:
            return False  # Has transactions, cannot delete
        
        cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def category_has_transactions(category_id):
    """Returns True if transactions exist for a given category ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# --- Transaction Functions ---

def insert_transaction(user_id, category_id, amount, t_type, note, date_str):
    """Inserts a new transaction record."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, category_id, amount, type, note, date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, category_id, amount, t_type, note.strip() if note else None, date_str)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def update_transaction(transaction_id, category_id, amount, t_type, note, date_str):
    """Updates an existing transaction."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE transactions SET category_id = ?, amount = ?, type = ?, note = ?, date = ? WHERE transaction_id = ?",
            (category_id, amount, t_type, note.strip() if note else None, date_str, transaction_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_transaction(transaction_id):
    """Deletes a transaction record."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_transactions(user_id, category_id=None, t_type=None, month=None, limit=None):
    """Fetches list of Transaction objects for the user based on filters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT t.*, c.name as category_name 
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
    """
    params = [user_id]
    
    if category_id:
        query += " AND t.category_id = ?"
        params.append(category_id)
    if t_type:
        query += " AND t.type = ?"
        params.append(t_type)
    if month:
        # month is format YYYY-MM, date is YYYY-MM-DD
        query += " AND strftime('%Y-%m', t.date) = ?"
        params.append(month)
        
    query += " ORDER BY t.date DESC, t.transaction_id DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        Transaction(
            transaction_id=r["transaction_id"],
            user_id=r["user_id"],
            category_id=r["category_id"],
            amount=r["amount"],
            type=r["type"],
            note=r["note"],
            date=r["date"],
            category_name=r["category_name"]
        ) for r in rows
    ]

def get_monthly_summary(user_id, month):
    """Calculates total income, total expenses, and balance for a user in a specific month."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions 
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        """,
        (user_id, month)
    )
    row = cursor.fetchone()
    conn.close()
    
    total_income = row["total_income"] or 0.0
    total_expense = row["total_expense"] or 0.0
    balance = total_income - total_expense
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }

# --- Budget Functions ---

def set_budget(user_id, category_id, month, limit_amount):
    """Inserts or updates a monthly limit for a specific category."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO budgets (user_id, category_id, month, limit_amount)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, category_id, month) 
            DO UPDATE SET limit_amount = excluded.limit_amount
            """,
            (user_id, category_id, month, limit_amount)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_budgets(user_id, month):
    """Fetches all budgets for a user in a specific month."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT b.*, c.name as category_name 
        FROM budgets b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.user_id = ? AND b.month = ?
        """,
        (user_id, month)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        Budget(
            budget_id=r["budget_id"],
            user_id=r["user_id"],
            category_id=r["category_id"],
            month=r["month"],
            limit_amount=r["limit_amount"],
            category_name=r["category_name"]
        ) for r in rows
    ]

def get_budget_status(user_id, month):
    """Returns budget limits vs actual spending for each category in the specified month."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # We want to select all expense categories, their budget limit (if set), and their actual spending.
    cursor.execute(
        """
        SELECT 
            c.category_id,
            c.name as category_name,
            COALESCE(b.limit_amount, 0) as limit_amount,
            COALESCE(SUM(t.amount), 0) as spent
        FROM categories c
        LEFT JOIN budgets b ON c.category_id = b.category_id AND b.month = ?
        LEFT JOIN transactions t ON c.category_id = t.category_id 
            AND t.user_id = c.user_id 
            AND strftime('%Y-%m', t.date) = ?
            AND t.type = 'expense'
        WHERE c.user_id = ? AND c.type = 'expense'
        GROUP BY c.category_id
        ORDER BY c.name ASC
        """,
        (month, month, user_id)
    )
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "category_id": r["category_id"],
            "category_name": r["category_name"],
            "limit_amount": r["limit_amount"],
            "spent": r["spent"],
            "is_over": r["spent"] > r["limit_amount"] if r["limit_amount"] > 0 else False,
            "percent": (r["spent"] / r["limit_amount"]) if r["limit_amount"] > 0 else 0.0
        })
    return results
