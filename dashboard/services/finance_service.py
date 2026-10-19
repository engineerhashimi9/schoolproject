"""
Finance & Accounting Service for School Management System
Handles revenue/expense metrics, financial balance sheets, and Afghan Dari currency wording.
"""

from typing import Dict, Any, List
from django.db.models import Sum, Count, F
from dashboard.models import Fee, Expense, Classes, Month, AcademiceYear, Student


def number_to_dari_words(number: int) -> str:
    """
    Convert an integer amount to authentic Dari/Persian words.
    e.g. 4500 -> "چهار هزار و پنجصد افغانی"
    """
    if number == 0:
        return "صفر افغانی"

    ones = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
    teens = ["ده", "یازده", "دوازده", "سیزده", "چهارده", "پانزده", "شانزده", "هفده", "هجده", "نوزده"]
    tens = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
    hundreds = ["", "یکصد", "دوصد", "سیصد", "چهارصد", "پنجصد", "ششصد", "هفتصد", "هشتصد", "نهصد"]

    def convert_chunk(n: int) -> str:
        parts = []
        c = n // 100
        rem = n % 100
        if c > 0:
            parts.append(hundreds[c])
        if rem >= 20:
            t = rem // 10
            o = rem % 10
            parts.append(tens[t])
            if o > 0:
                parts.append(ones[o])
        elif rem >= 10:
            parts.append(teens[rem - 10])
        elif rem > 0:
            parts.append(ones[rem])
        return " و ".join([p for p in parts if p])

    parts = []
    billions = number // 1_000_000_000
    rem = number % 1_000_000_000
    millions = rem // 1_000_000
    rem = rem % 1_000_000
    thousands = rem // 1_000
    last_chunk = rem % 1_000

    if billions > 0:
        parts.append(f"{convert_chunk(billions)} میلیارد")
    if millions > 0:
        parts.append(f"{convert_chunk(millions)} میلیون")
    if thousands > 0:
        parts.append(f"{convert_chunk(thousands)} هزار")
    if last_chunk > 0:
        parts.append(convert_chunk(last_chunk))

    result = " و ".join(parts)
    return f"{result} افغانی"


def calculate_finance_kpis(fees_list) -> Dict[str, Any]:
    """
    Calculate financial totals and collection ratios.
    """
    total_approved = sum(f.amount or 0 for f in fees_list)
    total_collected = sum(f.paied or 0 for f in fees_list)
    total_remaining = max(0, total_approved - total_collected)
    
    settlement_rate = round((total_collected / total_approved * 100), 1) if total_approved > 0 else 0.0
    
    fully_paid_count = sum(1 for f in fees_list if (f.paied or 0) >= (f.amount or 0))
    partial_paid_count = sum(1 for f in fees_list if 0 < (f.paied or 0) < (f.amount or 0))
    unpaid_count = sum(1 for f in fees_list if (f.paied or 0) == 0)
    indebted_count = partial_paid_count + unpaid_count

    return {
        "total_approved": total_approved,
        "total_collected": total_collected,
        "total_remaining": total_remaining,
        "settlement_rate": settlement_rate,
        "total_transactions": len(fees_list),
        "fully_paid_count": fully_paid_count,
        "partial_paid_count": partial_paid_count,
        "unpaid_count": unpaid_count,
        "indebted_count": indebted_count,
    }


def calculate_financial_report(academic_year: AcademiceYear) -> Dict[str, Any]:
    """
    Calculate master financial balance sheet (بیلان مالی عواید و مصارف):
    - Revenues from student fees
    - School expenditures (salaries, rent, utilities, maintenance, etc.)
    - Net profit / budget surplus or deficit
    """
    all_fees = list(Fee.objects.filter(academice_year=academic_year).select_related("student", "class_section", "month"))
    all_expenses = list(Expense.objects.filter(academice_year=academic_year).select_related("month"))

    total_revenue_approved = sum(f.amount or 0 for f in all_fees)
    total_revenue_collected = sum(f.paied or 0 for f in all_fees)
    total_outstanding_debt = max(0, total_revenue_approved - total_revenue_collected)

    total_expenses = sum(e.amount or 0 for e in all_expenses)

    # Net balance = collected cash - total expenses
    net_operating_balance = total_revenue_collected - total_expenses
    is_profit = net_operating_balance >= 0

    # Expense breakdown by category
    expense_categories = {}
    for exp in all_expenses:
        cat = exp.category or "متفرقه"
        expense_categories[cat] = expense_categories.get(cat, 0) + (exp.amount or 0)

    # Monthly breakdown
    months = list(Month.objects.all().order_by("id"))
    monthly_summary = []
    for m in months:
        m_fees = [f for f in all_fees if f.month_id == m.id]
        m_expenses = [e for e in all_expenses if e.month_id == m.id]
        
        m_rev = sum(f.paied or 0 for f in m_fees)
        m_exp = sum(e.amount or 0 for e in m_expenses)
        m_net = m_rev - m_exp
        
        if m_rev > 0 or m_exp > 0:
            monthly_summary.append({
                "month": m,
                "revenue": m_rev,
                "expense": m_exp,
                "net": m_net,
                "is_positive": m_net >= 0,
            })

    return {
        "academic_year": academic_year,
        "total_revenue_approved": total_revenue_approved,
        "total_revenue_collected": total_revenue_collected,
        "total_outstanding_debt": total_outstanding_debt,
        "total_expenses": total_expenses,
        "net_operating_balance": abs(net_operating_balance),
        "is_profit": is_profit,
        "expense_categories": expense_categories,
        "monthly_summary": monthly_summary,
        "fees_count": len(all_fees),
        "expenses_count": len(all_expenses),
    }
