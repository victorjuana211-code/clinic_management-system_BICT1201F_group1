"""
database.py
------------
Handles all SQLite database operations for the Clinic Management System:
- Database/table creation
- Seeding demo data (20+ records, plus a default login account)
- Authentication
- Search / filter queries for the dashboard
- Aggregate queries used by the charts module
- Date-range queries used by the PDF report module
"""

import sqlite3
import os
import random
import hashlib
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinic.db")

GENDERS = ["Male", "Female", "Other"]
STATUSES = ["Active", "Inactive", "Pending"]

FIRST_NAMES = [
    "Abu", "Fatmata", "Mohamed", "Aminata", "Ibrahim", "Mariama", "Sahr",
    "Isatu", "Joseph", "Adama", "Alhaji", "Hawa", "Foday", "Kadiatu",
    "Sorie", "Memunatu", "Daniel", "Zainab", "Emmanuel", "Yeabu"
]
LAST_NAMES = [
    "Kamara", "Sesay", "Bangura", "Koroma", "Conteh", "Turay", "Mansaray",
    "Sankoh", "Kargbo", "Jalloh", "Fofanah", "Sillah", "Bah", "Kanu"
]


def get_connection():
    """Return a new SQLite connection with rows accessible by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    """Simple SHA-256 hashing (sufficient for a school/demo project)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    """Create tables (if they don't exist) and seed demo data on first run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            status TEXT NOT NULL,
            created_date DATE NOT NULL,
            contact TEXT
        )
    """)
    conn.commit()

    # Seed a default login account
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", hash_password("admin123")),
        )
        conn.commit()

    # Seed demo records (at least 20, spread across the last 12 months)
    cur.execute("SELECT COUNT(*) FROM records")
    if cur.fetchone()[0] == 0:
        _seed_records(conn, count=30)

    conn.close()


def _seed_records(conn, count=30):
    cur = conn.cursor()
    today = datetime.now()
    rows = []
    for _ in range(count):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        gender = random.choice(GENDERS)
        status = random.choice(STATUSES)
        days_ago = random.randint(0, 365)
        created_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        contact = f"+232 7{random.randint(10000000, 99999999)}"
        rows.append((name, gender, status, created_date, contact))

    cur.executemany(
        """INSERT INTO records (full_name, gender, status, created_date, contact)
           VALUES (?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()


def verify_login(username, password):
    """Return True if the username/password combination is valid."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return False
    return row["password_hash"] == hash_password(password)


def _date_cutoff(date_filter):
    """Return a YYYY-MM-DD cutoff string for the 'Daily/Weekly/Monthly/Yearly' filter."""
    today = datetime.now()
    mapping = {
        "Daily": today,
        "Weekly": today - timedelta(days=7),
        "Monthly": today - timedelta(days=30),
        "Yearly": today - timedelta(days=365),
    }
    cutoff = mapping.get(date_filter)
    return cutoff.strftime("%Y-%m-%d") if cutoff else None


def fetch_records(search_term=None, gender=None, status=None, date_filter=None):
    """
    Fetch records from the database, applying:
      - a free-text search across ID, full name, and status
      - an exact-match gender filter
      - an exact-match status filter
      - a relative date filter (Daily / Weekly / Monthly / Yearly)
    """
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM records WHERE 1=1"
    params = []

    if search_term:
        query += " AND (full_name LIKE ? OR CAST(id AS TEXT) LIKE ? OR status LIKE ?)"
        like = f"%{search_term}%"
        params += [like, like, like]

    if gender and gender != "All":
        query += " AND gender = ?"
        params.append(gender)

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    if date_filter and date_filter != "All":
        cutoff = _date_cutoff(date_filter)
        if cutoff:
            query += " AND created_date >= ?"
            params.append(cutoff)

    query += " ORDER BY created_date DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_records_by_range(start_date, end_date):
    """Fetch all records whose created_date falls within [start_date, end_date]."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM records WHERE created_date BETWEEN ? AND ? ORDER BY created_date",
        (start_date, end_date),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_counts_by_field(field):
    """
    Return a dict of {value: count} for either 'gender' or 'status'.
    Field name is restricted to a safe whitelist to avoid SQL injection.
    """
    if field not in ("gender", "status"):
        raise ValueError("field must be 'gender' or 'status'")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {field} AS value, COUNT(*) AS count FROM records GROUP BY {field}")
    rows = cur.fetchall()
    conn.close()
    return {row["value"]: row["count"] for row in rows}


def get_monthly_registration_counts():
    """Return a list of (year-month, count) tuples ordered chronologically."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT strftime('%Y-%m', created_date) AS ym, COUNT(*) AS count
           FROM records GROUP BY ym ORDER BY ym"""
    )
    rows = cur.fetchall()
    conn.close()
    return [(row["ym"], row["count"]) for row in rows]


def get_weekly_activity_counts(weeks=8):
    """Return a list of (week_label, count) for the last N weeks (for the trend line)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT strftime('%Y-%W', created_date) AS wk, COUNT(*) AS count
           FROM records GROUP BY wk ORDER BY wk"""
    )
    rows = cur.fetchall()
    conn.close()
    data = [(row["wk"], row["count"]) for row in rows]
    return data[-weeks:] if len(data) > weeks else data


def get_yearly_growth_counts():
    """Return a list of (year, count) tuples ordered chronologically."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT strftime('%Y', created_date) AS yr, COUNT(*) AS count
           FROM records GROUP BY yr ORDER BY yr"""
    )
    rows = cur.fetchall()
    conn.close()
    return [(row["yr"], row["count"]) for row in rows]
