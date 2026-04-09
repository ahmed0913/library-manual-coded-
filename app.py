# ============================================
# Library Management System
# Author: Ahmed Yousif
#
# A simple Flask web application for managing
# a library's books, users, and categories.
# Powered by SQLite for zero-configuration testing.
# ============================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
import os
from functools import wraps

# ---- Load environment variables from .env file ----
load_dotenv()

# ---- Create the Flask application ----
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key')

# ---- File Upload Settings ----
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Max file size: 5MB

# Create the uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database path
DB_PATH = 'library.db'


# ---- Custom template filter ----
@app.template_filter('to_float')
def to_float_filter(value):
    """Convert a value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# ================================================
# DATABASE CONNECTION
# ================================================

def get_db():
    """
    Create and return a new SQLite database connection.
    Setting row_factory allows us to access columns by name (like dictionaries).
    """
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Build the tables automatically if they do not exist."""
    db = get_db()
    try:
        with open('database.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()


# ================================================
# HELPER FUNCTIONS
# ================================================

def allowed_file(filename):
    """Check if the uploaded file has an allowed image extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def log_activity(user_id, action_type, description):
    """Save an activity log to the database."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (user_id, action_type, description) VALUES (?, ?, ?)",
            (user_id, action_type, description)
        )
        db.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
    finally:
        db.close()


# ================================================
# DECORATORS (Access Control)
# ================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# ================================================
# ROUTES - Authentication
# ================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            db.close()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['name'] = user['name']
                session['role'] = user['role']

                log_activity(user['id'], 'login', f"User '{user['username']}' logged in")

                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            flash('An error occurred. Please try again.', 'danger')
            print(f"Login error: {e}")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not username or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        try:
            db = get_db()
            cursor = db.cursor()

            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                flash('Username already taken. Please choose another.', 'danger')
                db.close()
                return render_template('register.html')

            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, 'user')",
                (name, username, hashed_password)
            )
            db.commit()
            db.close()

            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'danger')
            print(f"Registration error: {e}")

    return render_template('register.html')


@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    username = session.get('username')

    if user_id:
        log_activity(user_id, 'logout', f"User '{username}' logged out")

    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ================================================
# ROUTES - Home Page
# ================================================

@app.route('/')
@login_required
def home():
    search_query = request.args.get('q', '').strip()
    search_by = request.args.get('search_by', 'title')

    try:
        db = get_db()
        cursor = db.cursor()

        if search_query:
            if search_by == 'author':
                cursor.execute(
                    """SELECT books.*, categories.name AS category_name
                       FROM books
                       LEFT JOIN categories ON books.category_id = categories.id
                       WHERE books.author LIKE ?
                       ORDER BY books.created_at DESC""",
                    (f'%{search_query}%',)
                )
            else:
                cursor.execute(
                    """SELECT books.*, categories.name AS category_name
                       FROM books
                       LEFT JOIN categories ON books.category_id = categories.id
                       WHERE books.title LIKE ?
                       ORDER BY books.created_at DESC""",
                    (f'%{search_query}%',)
                )
        else:
            cursor.execute(
                """SELECT books.*, categories.name AS category_name
                   FROM books
                   LEFT JOIN categories ON books.category_id = categories.id
                   ORDER BY books.created_at DESC"""
            )

        books = cursor.fetchall()
        db.close()

        return render_template('home.html', books=books,
                               search_query=search_query, search_by=search_by)
    except Exception as e:
        flash('Error loading books.', 'danger')
        print(f"Home page error: {e}")
        return render_template('home.html', books=[],
                               search_query='', search_by='title')


# ================================================
# ROUTES - Book Management
# ================================================

@app.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        price = request.form.get('price', 0)

        if not title or not author:
            flash('Title and Author are required.', 'danger')
            db.close()
            return render_template('add_book.html', categories=categories)

        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        try:
            if not category_id:
                category_id = None

            cursor.execute(
                """INSERT INTO books (title, author, description, category_id, price, image_path)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (title, author, description, category_id, float(price or 0), image_filename)
            )
            db.commit()
            log_activity(session['user_id'], 'add_book', f"Added book: '{title}'")
            db.close()

            flash(f'Book "{title}" added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash('Error adding book. Please try again.', 'danger')
            print(f"Add book error: {e}")

    db.close()
    return render_template('add_book.html', categories=categories)


@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        flash('Book not found.', 'danger')
        db.close()
        return redirect(url_for('home'))

    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        price = request.form.get('price', 0)

        if not title or not author:
            flash('Title and Author are required.', 'danger')
            db.close()
            return render_template('edit_book.html', book=book, categories=categories)

        image_filename = book['image_path']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                if book['image_path']:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], book['image_path'])
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        try:
            if not category_id:
                category_id = None

            cursor.execute(
                """UPDATE books
                   SET title=?, author=?, description=?, category_id=?, price=?, image_path=?
                   WHERE id=?""",
                (title, author, description, category_id, float(price or 0), image_filename, book_id)
            )
            db.commit()
            log_activity(session['user_id'], 'edit_book', f"Edited book: '{title}'")
            db.close()

            flash(f'Book "{title}" updated successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash('Error updating book. Please try again.', 'danger')
            print(f"Edit book error: {e}")

    db.close()
    return render_template('edit_book.html', book=book, categories=categories)


@app.route('/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()

        if not book:
            flash('Book not found.', 'danger')
            db.close()
            return redirect(url_for('home'))

        if book['image_path']:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], book['image_path'])
            if os.path.exists(image_path):
                os.remove(image_path)

        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        db.commit()
        log_activity(session['user_id'], 'delete_book', f"Deleted book: '{book['title']}'")
        db.close()

        flash(f'Book "{book["title"]}" deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting book. Please try again.', 'danger')
        print(f"Delete book error: {e}")

    return redirect(url_for('home'))


# ================================================
# ROUTES - Categories
# ================================================

@app.route('/categories')
@admin_required
def categories():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT categories.*, COUNT(books.id) AS book_count
               FROM categories
               LEFT JOIN books ON categories.id = books.category_id
               GROUP BY categories.id
               ORDER BY categories.name"""
        )
        categories_list = cursor.fetchall()
        db.close()

        return render_template('categories.html', categories=categories_list)
    except Exception as e:
        flash('Error loading categories.', 'danger')
        print(f"Categories error: {e}")
        return render_template('categories.html', categories=[])


@app.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('categories'))

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        db.commit()
        db.close()
        flash(f'Category "{name}" added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('This category already exists.', 'warning')
    except Exception as e:
        flash('Error adding category.', 'danger')
        print(f"Add category error: {e}")

    return redirect(url_for('categories'))


@app.route('/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM books WHERE category_id = ?", (category_id,))
        count = cursor.fetchone()['count']

        if count > 0:
            flash('Cannot delete — this category still has books.', 'warning')
        else:
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            db.commit()
            flash('Category deleted successfully!', 'success')

        db.close()
    except Exception as e:
        flash('Error deleting category.', 'danger')
        print(f"Delete category error: {e}")

    return redirect(url_for('categories'))


# ================================================
# ROUTES - Users
# ================================================

@app.route('/users')
@admin_required
def users():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, name, username, role, created_at FROM users ORDER BY created_at DESC"
        )
        users_list = cursor.fetchall()
        db.close()

        return render_template('users.html', users=users_list)
    except Exception as e:
        flash('Error loading users.', 'danger')
        print(f"Users error: {e}")
        return render_template('users.html', users=[])


@app.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('users'))

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            flash('User not found.', 'danger')
        else:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            db.commit()
            flash(f'User "{user["username"]}" deleted successfully!', 'success')

        db.close()
    except Exception as e:
        flash('Error deleting user.', 'danger')
        print(f"Delete user error: {e}")

    return redirect(url_for('users'))


# ================================================
# ROUTES - Dashboard & Logs
# ================================================

@app.route('/dashboard')
@admin_required
def dashboard():
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) AS count FROM books")
        total_books = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM users")
        total_users = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) AS count FROM categories")
        total_categories = cursor.fetchone()['count']

        cursor.execute(
            """SELECT activity_logs.*, users.username
               FROM activity_logs
               LEFT JOIN users ON activity_logs.user_id = users.id
               ORDER BY activity_logs.timestamp DESC
               LIMIT 20"""
        )
        recent_logs = cursor.fetchall()
        db.close()

        return render_template('dashboard.html',
                               total_books=total_books,
                               total_users=total_users,
                               total_categories=total_categories,
                               recent_logs=recent_logs)
    except Exception as e:
        flash('Error loading dashboard.', 'danger')
        print(f"Dashboard error: {e}")
        return render_template('dashboard.html',
                               total_books=0, total_users=0,
                               total_categories=0, recent_logs=[])


@app.route('/logs')
@admin_required
def logs():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """SELECT activity_logs.*, users.username
               FROM activity_logs
               LEFT JOIN users ON activity_logs.user_id = users.id
               ORDER BY activity_logs.timestamp DESC
               LIMIT 100"""
        )
        logs_list = cursor.fetchall()
        db.close()

        return render_template('logs.html', logs=logs_list)
    except Exception as e:
        flash('Error loading logs.', 'danger')
        print(f"Logs error: {e}")
        return render_template('logs.html', logs=[])


# ================================================
# RUN THE APPLICATION
# ================================================

if __name__ == '__main__':
    # Initialize the database and create tables if they do not exist!
    init_db()
    
    app.run(debug=True, port=5000)
