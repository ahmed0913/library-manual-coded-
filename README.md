# 📚 Library Management System
A Beginner-Friendly, Full-Stack Library Management System

**Flask · SQLite · HTML/CSS/JS**

Developed by **Ahmed Yousif**

---

## 📖 Table of Contents
- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Database Schema](#-database-schema)
- [Role and Permission Matrix](#-role-and-permission-matrix)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Setup and Installation](#-setup-and-installation)
- [Default Credentials](#-default-credentials)
- [Frontend Pages](#-frontend-pages)

---

## 🧠 Overview
A clean, production-ready Library Management System designed specifically to be simple, standalone, and easy to understand for first-year students. The system supports two user roles (Admin and User), manages the book catalog, categorizes items, and maintains a full audit trail of all system activities.

**Note:** Registration is open, but new users default to the 'User' role. The Admin role has exclusive control over the library's management.

### Key Highlights
| Feature | Description |
|---------|-------------|
| 🔐 **Session Authentication** | Secure, server-side session-based login with password hashing. |
| 👥 **Role-Based Access** | Granular permissions per role (Admin / User). |
| 📖 **Book Catalog** | Grid display with cover images, dynamic search, and category filtering. |
| 📝 **Activity Logs** | Complete audit trail of all CRUD operations (Add, Edit, Delete). |
| 📊 **Dashboard** | Live statistics and recent activity feed for administrators. |
| 🚀 **Zero Configuration** | Uses built-in SQLite. Works out of the box with no external database servers needed. |

---

## 🏗 System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Web Browser)                       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ HTML/CSS │  │ Vanilla JS   │  │ Jinja2 Templates      │  │
│  └────┬─────┘  └──────┬───────┘  └───────────┬───────────┘  │
└───────│───────────────│──────────────────────│──────────────┘
        │               │                      │
        ▼               ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask Monolith)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Session Auth │─▶│  Decorators  │─▶│   Flask Routes    │  │
│  └──────────────┘  └──────────────┘  └────────┬──────────┘  │
│                                                │             │
│    Routes: auth, books, users, categories,     │             │
│    dashboard, activity_logs                    │             │
└────────────────────────────────────────────────┬─────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE (SQLite Built-in)                   │
│                                                              │
│   users · books · categories · activity_logs                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗃 Database Schema

### Tables and Relationships
```text
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    USERS     │       │  CATEGORIES  │       │    BOOKS     │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id      (PK) │       │ id      (PK) │       │ id      (PK) │
│ name         │       │ name    (UK) │       │ title        │
│ username (UK)│       │ created_at   │       │ author       │
│ password     │       └──────┬───────┘       │ description  │
│ role         │              │               │ category_id(FK)
│ created_at   │              │ 1:N           │ price        │
└──────┬───────┘              │               │ image_path   │
       │                      └──────────────▶│ created_at   │
       │                                      └──────────────┘
       │ 1:N                                           
       │                                               
       ▼                                               
┌──────────────┐
│ACTIVITY_LOGS │
├──────────────┤
│ id      (PK) │
│ user_id (FK) │
│ action_type  │
│ description  │
│ timestamp    │
└──────────────┘
```

---

## 🛡 Role and Permission Matrix

| Action | Admin | User |
|--------|-------|------|
| View Dashboard Statistics | ✅ | ❌ |
| Manage Users (Delete) | ✅ | ❌ |
| Manage Categories (Add, Delete) | ✅ | ❌ |
| Manage Books (Add, Edit, Delete) | ✅ | ❌ |
| View Books Catalog & Search | ✅ | ✅ |
| View System Activity Logs | ✅ | ❌ |

---

## 📂 Project Structure

```text
DB_WEB/
│
├── app.py                      # Main Flask App & Routing (Monolithic)
├── database.sql                # SQL Schema definition
├── seed.py                     # Script to seed default data & Admin user
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows startup script
│
├── static/                     # Frontend Assets
│   ├── css/
│   │   └── style.css           # Global Dark Theme design system
│   ├── js/
│   │   └── main.js             # Client-side interactions
│   └── uploads/                # Book cover image storage
│
└── templates/                  # Jinja2 HTML Templates
    ├── base.html               # Master layout (Navbar, Footer, Flash msgs)
    ├── login.html              # Authentication
    ├── register.html           # User registration
    ├── home.html               # Main book catalog
    ├── dashboard.html          # Admin stats
    ├── books/                  # Book forms (add/edit)
    └── admin/                  # Admin views (Users, Categories, Logs)
```

---

## 🛠 Tech Stack

### Framework & Database
| Standard | Technology | Purpose |
|----------|------------|---------|
| Backend | **Flask (Python)** | Web framework handling routes and logic |
| Database| **SQLite** | Built-in zero-config database |
| Security| **Werkzeug** | Secure password hashing (`pbkdf2:sha256`) |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Styling | **Vanilla CSS** | Custom Dark Theme layout & responsiveness |
| Structure | **Jinja2 / HTML5**| Server-side HTML rendering |
| Logic | **Vanilla JS** | Micro-interactions (Menu toggles, Image previews) |

---

## 🚀 Setup and Installation

Because this system uses SQLite, **no external database servers (like XAMPP or MySQL) are required.**

### Prerequisites
- Python 3.9+ installed on your machine.

### Windows Easy Startup (Recommended)
1. Double-click the **`run.bat`** file in the project folder.
2. The script will automatically:
   - Verify the virtual environment.
   - Start the Flask backend.
   - Open your default web browser to the application.

### Manual Startup (Any OS)
If you prefer running commands manually:
```bash
# 1. Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database (creates tables & admin user automatically)
python seed.py

# 4. Run the app
python app.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🔑 Default Credentials

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |
| Role | Admin |

*(These credentials are automatically generated upon the first run of the project).*

---

## 🖥 Frontend Pages

| Page | Access | Description |
|------|--------|-------------|
| **Login** | Public | Session creation via username/password |
| **Register** | Public | Create a standard user account |
| **Home (Books)** | All | Responsive card grid with search capabilities |
| **Dashboard** | Admin | High-level statistics on books, users, and categories |
| **Add Book** | Admin | Form with cover image upload handling |
| **Edit Book** | Admin | Pre-filled modification form |
| **Categories** | Admin | Management of book groupings |
| **Users** | Admin | Overview of registered members with deletion capability |
| **Activity Logs** | Admin | Audit trail of CRUD actions performed in the system |

---
**Copyright © 2026 Ahmed Yousif. All rights reserved.**
