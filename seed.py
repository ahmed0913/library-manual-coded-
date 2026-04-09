import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = 'library.db'

def seed_database():
    """Build the database and seed it with an admin user and categories."""
    
    # 1. Read the schema from database.sql
    try:
        with open('database.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print("Error: database.sql not found!")
        return

    # 2. Connect to SQLite database (this will create library.db if it doesn't exist)
    print(f"Connecting to SQLite database at {DB_PATH}...")
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    try:
        # 3. Create tables
        print("Creating tables...")
        cursor.executescript(sql_script)

        # 4. Create default categories
        categories = ['Programming', 'Science Fiction', 'History', 'Art & Design', 'Business']
        print("Adding default categories...")
        for cat in categories:
            try:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
            except sqlite3.IntegrityError:
                # Category already exists, skip
                pass

        # 5. Create admin user
        print("Creating admin user...")
        admin_username = 'admin'
        admin_password = 'admin123'
        hashed_password = generate_password_hash(admin_password)

        try:
            cursor.execute(
                "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, 'admin')",
                ('System Administrator', admin_username, hashed_password)
            )
            print(f"[OK] Admin user created successfully!")
            print(f"   Username: {admin_username}")
            print(f"   Password: {admin_password}")
        except sqlite3.IntegrityError:
            print(f"[INFO] Admin user '{admin_username}' already exists.")

        # Commit changes
        db.commit()
        print("\n[SUCCESS] Database seeded successfully! You can now run 'python app.py'")

    except sqlite3.Error as err:
        print(f"[ERROR] Database error: {err}")
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    seed_database()
