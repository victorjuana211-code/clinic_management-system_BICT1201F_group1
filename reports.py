"""
reports.py
----------
Generates downloadable PDF reports (Weekly / Monthly / Yearly) containing:
  - Report title and date range
  - Summary statistics
  - A table of matching records
  - Generated date and time

Requires: reportlab (pip install reportlab)
"""

from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import database as db


def get_date_range(report_type, reference_date):
    """
    Compute the (start_date, end_date) strings (YYYY-MM-DD) for the given
    report_type ('Weekly', 'Monthly', 'Yearly') relative to reference_date.
    """
    if report_type == "Weekly":
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=6)

    elif report_type == "Monthly":
        start = reference_date.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        end = next_month - timedelta(days=1)

    elif report_type == "Yearly":
        start = reference_date.replace(month=1, day=1)
        end = reference_date.replace(month=12, day=31)

    else:
        raise ValueError("report_type must be 'Weekly', 'Monthly', or 'Yearly'")

    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _build_summary_table(records):
    total = len(records)
    active = sum(1 for r in records if r["status"] == "Active")
    inactive = sum(1 for r in records if r["status"] == "Inactive")
    pending = sum(1 for r in records if r["status"] == "Pending")
    male = sum(1 for r in records if r["gender"] == "Male")
    female = sum(1 for r in records if r["gender"] == "Female")
    other = sum(1 for r in records if r["gender"] == "Other")

    data = [
        ["Metric", "Count"],
        ["Total Records", str(total)],
        ["Active", str(active)],
        ["Inactive", str(inactive)],
        ["Pending", str(pending)],
        ["Male", str(male)],
        ["Female", str(female)],
        ["Other", str(other)],
    ]
    table = Table(data, colWidths=[8 * cm, 4 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    return table


def _build_records_table(records):
    header = ["ID", "Full Name", "Gender", "Status", "Date Created", "Contact"]
    data = [header]
    for r in records:
        data.append([
            str(r["id"]), r["full_name"], r["gender"],
            r["status"], r["created_date"], r["contact"] or ""
        ])

    table = Table(
        data,
        colWidths=[1.5 * cm, 5 * cm, 2.3 * cm, 2.3 * cm, 3 * cm, 4 * cm],
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def generate_report(filepath, report_type, start_date, end_date):
    """
    Build a PDF report at `filepath` for records created between
    start_date and end_date (both 'YYYY-MM-DD' strings).
    """
    records = db.fetch_records_by_range(start_date, end_date)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=18, spaceAfter=6
    )

    elements = []
    elements.append(Paragraph(f"{report_type} Report &ndash; Clinic Management System", title_style))
    elements.append(Paragraph(f"Date Range: {start_date} to {end_date}", styles["Normal"]))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]
    ))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Summary Statistics", styles["Heading2"]))
    elements.append(_build_summary_table(records))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Records", styles["Heading2"]))
    if records:
        elements.append(_build_records_table(records))
    else:
        elements.append(Paragraph(
            "No records were found for the selected date range.", styles["Normal"]
        ))

    doc.build(elements)
    return filepath
