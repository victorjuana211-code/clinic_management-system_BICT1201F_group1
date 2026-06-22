"""
main.py
-------
Entry point for the Clinic Management System.

Run with:
    python main.py
"""

import database as db
from app import LoginWindow


def main():
    db.init_db()
    login_window = LoginWindow()
    login_window.mainloop()


if __name__ == "__main__":
    main()
