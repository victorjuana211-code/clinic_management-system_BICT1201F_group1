"""
charts.py
---------
Data Visualization Dashboard: a Toplevel window with three tabs
(Bar Chart, Pie Chart, Line Graph) built with matplotlib, embedded
inside Tkinter using FigureCanvasTkAgg.

Requires: matplotlib (pip install matplotlib)
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database as db


class ChartsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Data Visualization Dashboard")
        self.geometry("950x680")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.bar_tab = ttk.Frame(notebook)
        self.pie_tab = ttk.Frame(notebook)
        self.line_tab = ttk.Frame(notebook)

        notebook.add(self.bar_tab, text="Bar Chart")
        notebook.add(self.pie_tab, text="Pie Chart")
        notebook.add(self.line_tab, text="Line Graph")

        self._build_bar_chart()
        self._build_pie_chart()
        self._build_line_chart()

    # ---------- Bar Chart: records by status / gender ----------
    def _build_bar_chart(self):
        fig = Figure(figsize=(8, 5), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        status_counts = db.get_counts_by_field("status")
        ax1.bar(list(status_counts.keys()), list(status_counts.values()),
                color=["#2E75B6", "#DD8452", "#55A868"])
        ax1.set_title("Records by Status")
        ax1.set_ylabel("Number of Records")

        gender_counts = db.get_counts_by_field("gender")
        ax2.bar(list(gender_counts.keys()), list(gender_counts.values()),
                color=["#4C72B0", "#C44E52", "#8172B2"])
        ax2.set_title("Records by Gender")
        ax2.set_ylabel("Number of Records")

        fig.tight_layout()
        self._embed(fig, self.bar_tab)

    # ---------- Pie Chart: gender / status distribution ----------
    def _build_pie_chart(self):
        fig = Figure(figsize=(8, 5), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        gender_counts = db.get_counts_by_field("gender")
        ax1.pie(list(gender_counts.values()), labels=list(gender_counts.keys()),
                autopct="%1.1f%%", startangle=90)
        ax1.set_title("Gender Distribution")

        status_counts = db.get_counts_by_field("status")
        ax2.pie(list(status_counts.values()), labels=list(status_counts.keys()),
                autopct="%1.1f%%", startangle=90)
        ax2.set_title("Status Distribution")

        fig.tight_layout()
        self._embed(fig, self.pie_tab)

    # ---------- Line Graph: registration trends over time ----------
    def _build_line_chart(self):
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        monthly = db.get_monthly_registration_counts()
        if monthly:
            months = [m for m, _ in monthly]
            counts = [c for _, c in monthly]
            ax.plot(months, counts, marker="o", color="#2E75B6", linewidth=2)
        else:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")

        ax.set_title("Monthly Record Registrations")
        ax.set_xlabel("Month")
        ax.set_ylabel("Registrations")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        self._embed(fig, self.line_tab)

    @staticmethod
    def _embed(fig, parent):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
