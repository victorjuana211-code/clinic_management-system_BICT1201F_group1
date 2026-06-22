"""
app.py
------
Tkinter GUI for the Clinic Management System:

  - LoginWindow    : username/password login with validation and a
                      "Forgot Password" helper dialog.
  - DashboardWindow: record list (Treeview), live search, filters
                      (gender / status / date), and buttons to open the
                      charts window and the PDF report dialog.
  - ReportDialog    : lets the user pick a report type (Weekly / Monthly /
                      Yearly) and a reference date, then saves a PDF.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import database as db
import reports
from charts import ChartsWindow


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Management System - Login")
        self.geometry("420x340")
        self.resizable(False, False)
        self.configure(bg="#1F3B57")

        container = tk.Frame(self, bg="#1F3B57")
        container.pack(expand=True)

        tk.Label(container, text="Clinic Management System",
                 font=("Helvetica", 16, "bold"), bg="#1F3B57", fg="white").pack(pady=(25, 6))
        tk.Label(container, text="Please sign in to continue",
                 font=("Helvetica", 10), bg="#1F3B57", fg="#CBD8E5").pack(pady=(0, 20))

        form = tk.Frame(container, bg="#1F3B57")
        form.pack()

        tk.Label(form, text="Username", bg="#1F3B57", fg="white").grid(
            row=0, column=0, sticky="w", pady=6)
        self.username_var = tk.StringVar()
        tk.Entry(form, textvariable=self.username_var, width=28).grid(
            row=0, column=1, pady=6, padx=8)

        tk.Label(form, text="Password", bg="#1F3B57", fg="white").grid(
            row=1, column=0, sticky="w", pady=6)
        self.password_var = tk.StringVar()
        tk.Entry(form, textvariable=self.password_var, show="*", width=28).grid(
            row=1, column=1, pady=6, padx=8)

        self.error_label = tk.Label(container, text="", fg="#FF8A80", bg="#1F3B57")
        self.error_label.pack(pady=(8, 0))

        tk.Button(container, text="Login", command=self.attempt_login, width=22,
                  bg="#2E75B6", fg="white", relief="flat", cursor="hand2").pack(pady=16)
        tk.Button(container, text="Forgot Password?", command=self.forgot_password,
                  bg="#1F3B57", fg="#9FC1E0", relief="flat", bd=0,
                  cursor="hand2").pack()

        tk.Label(container, text="Demo login: admin / admin123",
                 font=("Helvetica", 8), bg="#1F3B57", fg="#6F87A0").pack(pady=(20, 0))

        self.bind("<Return>", lambda event: self.attempt_login())

    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.error_label.config(text="Please enter both username and password.")
            return

        if db.verify_login(username, password):
            self.destroy()
            DashboardWindow().mainloop()
        else:
            self.error_label.config(text="Invalid username or password.")
            self.password_var.set("")

    def forgot_password(self):
        messagebox.showinfo(
            "Forgot Password",
            "Please contact your system administrator to reset your password.\n\n"
            "Demo credentials for this project:\nUsername: admin\nPassword: admin123",
        )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Management System - Dashboard")
        self.geometry("1150x650")
        self.minsize(950, 550)

        self._build_top_bar()
        self._build_filter_bar()
        self._build_table()
        self.load_records()

    # ----- UI sections -----
    def _build_top_bar(self):
        top = tk.Frame(self, bg="#2E75B6")
        top.pack(fill="x")

        tk.Label(top, text="Clinic Management Dashboard", font=("Helvetica", 16, "bold"),
                 bg="#2E75B6", fg="white").pack(side="left", padx=20, pady=15)

        button_frame = tk.Frame(top, bg="#2E75B6")
        button_frame.pack(side="right", padx=20)

        tk.Button(button_frame, text="Charts", command=self.open_charts,
                  bg="white", fg="#2E75B6", relief="flat", width=12,
                  cursor="hand2").pack(side="left", padx=4)
        tk.Button(button_frame, text="Generate PDF Report", command=self.open_report_dialog,
                  bg="white", fg="#2E75B6", relief="flat", width=18,
                  cursor="hand2").pack(side="left", padx=4)
        tk.Button(button_frame, text="Logout", command=self.logout,
                  bg="#1F3B57", fg="white", relief="flat", width=10,
                  cursor="hand2").pack(side="left", padx=4)

    def _build_filter_bar(self):
        bar = tk.Frame(self, pady=12, padx=20)
        bar.pack(fill="x")

        tk.Label(bar, text="Search:").grid(row=0, column=0, padx=4)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(bar, textvariable=self.search_var, width=24)
        search_entry.grid(row=0, column=1, padx=4)
        search_entry.bind("<KeyRelease>", lambda e: self.load_records())

        tk.Label(bar, text="Gender:").grid(row=0, column=2, padx=4)
        self.gender_var = tk.StringVar(value="All")
        gender_box = ttk.Combobox(bar, textvariable=self.gender_var, width=10, state="readonly",
                                   values=["All", "Male", "Female", "Other"])
        gender_box.grid(row=0, column=3, padx=4)
        gender_box.bind("<<ComboboxSelected>>", lambda e: self.load_records())

        tk.Label(bar, text="Status:").grid(row=0, column=4, padx=4)
        self.status_var = tk.StringVar(value="All")
        status_box = ttk.Combobox(bar, textvariable=self.status_var, width=10, state="readonly",
                                   values=["All", "Active", "Inactive", "Pending"])
        status_box.grid(row=0, column=5, padx=4)
        status_box.bind("<<ComboboxSelected>>", lambda e: self.load_records())

        tk.Label(bar, text="Date:").grid(row=0, column=6, padx=4)
        self.date_var = tk.StringVar(value="All")
        date_box = ttk.Combobox(bar, textvariable=self.date_var, width=10, state="readonly",
                                 values=["All", "Daily", "Weekly", "Monthly", "Yearly"])
        date_box.grid(row=0, column=7, padx=4)
        date_box.bind("<<ComboboxSelected>>", lambda e: self.load_records())

        tk.Button(bar, text="Reset Filters", command=self.reset_filters).grid(
            row=0, column=8, padx=10)

    def _build_table(self):
        table_frame = tk.Frame(self, padx=20, pady=4)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "full_name", "gender", "created_date", "status", "contact")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        headings = {
            "id": "Record ID", "full_name": "Full Name", "gender": "Gender",
            "created_date": "Date Created", "status": "Status",
            "contact": "Contact Information",
        }
        widths = {
            "id": 80, "full_name": 220, "gender": 100,
            "created_date": 120, "status": 100, "contact": 180,
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.count_label = tk.Label(self, text="", anchor="w", padx=20, pady=6)
        self.count_label.pack(fill="x")

    # ----- Behaviour -----
    def load_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        records = db.fetch_records(
            search_term=self.search_var.get().strip(),
            gender=self.gender_var.get(),
            status=self.status_var.get(),
            date_filter=self.date_var.get(),
        )
        for r in records:
            self.tree.insert("", "end", values=(
                r["id"], r["full_name"], r["gender"],
                r["created_date"], r["status"], r["contact"],
            ))

        self.count_label.config(text=f"Showing {len(records)} record(s)")

    def reset_filters(self):
        self.search_var.set("")
        self.gender_var.set("All")
        self.status_var.set("All")
        self.date_var.set("All")
        self.load_records()

    def open_charts(self):
        ChartsWindow(self)

    def open_report_dialog(self):
        ReportDialog(self)

    def logout(self):
        self.destroy()
        LoginWindow().mainloop()


# ---------------------------------------------------------------------------
# PDF report dialog
# ---------------------------------------------------------------------------
class ReportDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Generate PDF Report")
        self.geometry("380x280")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        tk.Label(self, text="Select Report Type", font=("Helvetica", 11, "bold")).pack(
            pady=(18, 6))
        self.report_type_var = tk.StringVar(value="Weekly")
        ttk.Combobox(self, textvariable=self.report_type_var, state="readonly",
                     values=["Weekly", "Monthly", "Yearly"], width=20).pack(pady=4)

        tk.Label(self, text="Reference Date (YYYY-MM-DD)").pack(pady=(16, 6))
        self.ref_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(self, textvariable=self.ref_date_var, width=22, justify="center").pack(pady=4)

        tk.Label(self, text="The report covers the full week / month / year\n"
                             "that contains the reference date.",
                 font=("Helvetica", 8), fg="#555555").pack(pady=(8, 0))

        tk.Button(self, text="Generate Report", command=self.generate, bg="#2E75B6",
                  fg="white", relief="flat", width=22, cursor="hand2").pack(pady=20)

    def generate(self):
        try:
            ref_date = datetime.strptime(self.ref_date_var.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return

        report_type = self.report_type_var.get()
        start_date, end_date = reports.get_date_range(report_type, ref_date)

        default_name = f"{report_type}_Report_{ref_date.strftime('%Y%m%d')}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if not filepath:
            return

        reports.generate_report(filepath, report_type, start_date, end_date)
        messagebox.showinfo("Report Generated", f"Report saved successfully:\n{filepath}")
        self.destroy()
