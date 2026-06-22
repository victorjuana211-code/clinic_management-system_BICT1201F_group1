# Clinic Management System

A GUI-based clinic record management system built with Python, Tkinter, and
SQLite, developed using structured programming principles (sequence,
selection, iteration, and modular functions).

## Features

- **Login Page** — username/password authentication with validation and a
  "Forgot Password" helper dialog.
- **Records Management** — 30 demo records preloaded (minimum requirement: 20),
  each with Record ID, Full Name, Gender, Date Created, Status, and Contact
  Information.
- **Dashboard** — search by name, ID, or status; filter by gender, status,
  and date range (Daily / Weekly / Monthly / Yearly).
- **Data Visualization Dashboard** — Bar Chart (records by status/gender),
  Pie Chart (gender/status distribution), and Line Graph (monthly
  registration trend), built with matplotlib and embedded in the GUI.
- **PDF Report Generation** — downloadable Weekly, Monthly, or Yearly
  reports with a title, date range, summary statistics, a table of
  records, and a generated timestamp.
- **SQLite Database** — all data is stored in `clinic.db`, created
  automatically on first run.

## Project Structure

```
clinic_management_system/
├── main.py          # Entry point — run this file
├── app.py           # Login window + Dashboard window (Tkinter GUI)
├── charts.py         # Bar / Pie / Line chart window (matplotlib)
├── reports.py        # PDF report generation (reportlab)
├── database.py        # SQLite setup, seeding, and queries
├── requirements.txt   # Third-party dependencies
└── README.md
```

## Setup

1. Make sure you have **Python 3.9+** installed.
   - Tkinter ships with most Python installations. On some Linux
     distributions you may need to install it separately:
     `sudo apt install python3-tk`
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Demo Login

```
Username: admin
Password: admin123
```

The database (`clinic.db`) and this default account are created
automatically the first time you run `main.py`. Demo records are
randomly generated with dates spread across the last 12 months so that
the filters and charts have realistic data to display.

## Notes for the group project

- The SQL schema matches the brief's example:
  ```sql
  CREATE TABLE records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      full_name TEXT NOT NULL,
      gender TEXT NOT NULL,
      status TEXT NOT NULL,
      created_date DATE NOT NULL
  );
  ```
  (a `contact` column was added to satisfy the "Contact Information"
  field requirement).
- To add your own records instead of the random demo data, delete
  `clinic.db` and edit `_seed_records()` in `database.py` before
  running the app again — or add an "Add Record" form to `app.py` if
  your brief requires manual entry through the GUI.
- Passwords are stored as SHA-256 hashes rather than plain text, which
  you can mention under "Open Source and Ethical Considerations" in
  your report.
