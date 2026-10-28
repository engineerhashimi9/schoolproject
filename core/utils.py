"""
Core Utilities for School Management System (سامانه مدیریت تعلیمی مکاتب افغانستان)
Shared helpers for Jalali calendar, academic year resolution, and formatting.
"""

import jdatetime
from typing import Optional


JALALI_MONTH_NAMES = [
    "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
]


def get_current_jalali_date_str() -> str:
    """
    Returns current date formatted in Jalali calendar (e.g. '۲۷ عقرب ۱۴۰۳').
    """
    try:
        now_j = jdatetime.date.today()
        month_name = JALALI_MONTH_NAMES[now_j.month - 1]
        return f"{now_j.day} {month_name} {now_j.year}"
    except Exception:
        return "۱۴۰۳"


def get_active_academic_year(year_val: int = 1403):
    """
    Resolves the active academic year instance, defaulting to 1403 or latest.
    """
    from dashboard.models import AcademiceYear
    return (
        AcademiceYear.objects.filter(year=year_val).first()
        or AcademiceYear.objects.order_by("-year").first()
    )


def format_afghan_currency(amount: float) -> str:
    """
    Formats numerical amounts with comma separators and Afghan Afghani suffix.
    """
    try:
        val = int(amount)
        return f"{val:,} افغانی"
    except (ValueError, TypeError):
        return "۰ افغانی"
