import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dashboard.models import Fee, Expense, Student, Classes, AcademiceYear, Month
from dashboard.services.finance_service import number_to_dari_words

User = get_user_model()

def run_tests():
    print("=== STARTING FINANCE MODULE AUTOMATED TESTS ===")

    # 1. Test Dari Currency Words
    assert number_to_dari_words(0) == "صفر افغانی", "Failed 0"
    assert "چهار هزار و پنجصد افغانی" in number_to_dari_words(4500), "Failed 4500"
    assert "صد و بیست هزار افغانی" in number_to_dari_words(120000) or "یکصد و بیست هزار افغانی" in number_to_dari_words(120000), "Failed 120000"
    print("✓ number_to_dari_words: PASSED")

    # 2. Setup Client & Admin User
    client = Client()
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser("testadmin", "admin@school.af", "pass123")
    client.force_login(admin_user)
    print(f"✓ Authenticated as admin: {admin_user.email}")

    # 3. Test Finance List View
    url_list = reverse("dashboard:finance-list")
    resp = client.get(url_list)
    assert resp.status_code == 200, f"Expected 200 on finance-list, got {resp.status_code}"
    assert "kpis" in resp.context, "kpis missing in context"
    assert "fees" in resp.context, "fees missing in context"
    assert "students_for_modal" in resp.context, "students_for_modal missing"
    print(f"✓ FinanceListView: PASSED (Loaded {len(resp.context['fees'])} fees, Total Approved: {resp.context['kpis']['total_approved']} AFN)")

    # 4. Test Filter on Finance List
    resp_filter = client.get(url_list, {"fee_type": "1"})
    assert resp_filter.status_code == 200
    print("✓ FinanceListView filter (fee_type=1): PASSED")

    # 5. Test Fee Create
    student = Student.objects.filter(status__id=1).first()
    month = Month.objects.first()
    year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
    cls = Classes.objects.first()

    url_create = reverse("dashboard:fee-create")
    post_data = {
        "student_id": student.id,
        "class_id": cls.id,
        "month_id": month.id,
        "year_id": year.id,
        "amount": "5000",
        "paied": "3500",
        "payment_date": "2024-10-15",
        "payment_method": "نقدی (صندوق مکتب)",
        "fee_category": "شهریه ماهوار",
        "receipt_number": "REC-TEST-9999",
        "notes": "تست پرداخت آزمایشی",
        "action": "save",
    }
    resp_create = client.post(url_create, post_data)
    assert resp_create.status_code == 302, f"Expected 302 redirect, got {resp_create.status_code}"

    created_fee = Fee.objects.filter(receipt_number="REC-TEST-9999").first()
    assert created_fee is not None, "Created fee not found in database!"
    assert created_fee.amount == 5000, "Amount mismatch"
    assert created_fee.paied == 3500, "Paied mismatch"
    assert created_fee.remaining == 1500, "Remaining calculation incorrect"
    assert created_fee.status_label == "پرداخت قسطی", f"Unexpected status label: {created_fee.status_label}"
    print(f"✓ fee_create: PASSED (Created Fee ID {created_fee.id}, Remaining: {created_fee.remaining} AFN)")

    # 6. Test Fee Receipt View
    url_receipt = reverse("dashboard:fee-receipt", kwargs={"id": created_fee.id})
    resp_receipt = client.get(url_receipt)
    assert resp_receipt.status_code == 200, f"Expected 200 on fee-receipt, got {resp_receipt.status_code}"
    html_content = resp_receipt.content.decode("utf-8")
    assert "سه هزار و پنجصد افغانی" in html_content, "Dari words paied amount not found in receipt HTML"
    assert "REC-TEST-9999" in html_content, "Receipt number not found in receipt HTML"
    print("✓ fee_receipt_view: PASSED (Dari words and receipt details rendered properly)")

    # 7. Test Fee Edite View
    url_edite = reverse("dashboard:fee-edite", kwargs={"id": created_fee.id})
    resp_edite_get = client.get(url_edite)
    assert resp_edite_get.status_code == 200, "Expected 200 on fee-edite GET"

    edit_data = {
        "class_id": cls.id,
        "month_id": month.id,
        "year_id": year.id,
        "amount": "5000",
        "paied": "5000",  # changed to full payment
        "payment_date": "2024-10-15",
        "payment_method": "واریز به حساب بانکی",
        "fee_category": "شهریه ماهوار",
        "receipt_number": "REC-TEST-9999",
        "notes": "اصلاح شد و تسویه گردید",
    }
    resp_edite_post = client.post(url_edite, edit_data)
    assert resp_edite_post.status_code == 302, f"Expected 302 on fee-edite POST, got {resp_edite_post.status_code}"

    created_fee.refresh_from_db()
    assert created_fee.paied == 5000, "Fee paied did not update"
    assert created_fee.remaining == 0, "Fee remaining not 0"
    assert created_fee.status_label == "تسویه کامل", f"Status label should be تسویه کامل, got {created_fee.status_label}"
    print("✓ fee_edite: PASSED (Updated fee to full payment)")

    # 8. Test Expenses View (GET & POST)
    url_exp = reverse("dashboard:finance-expenses")
    resp_exp = client.get(url_exp)
    assert resp_exp.status_code == 200, f"Expected 200 on expenses_view, got {resp_exp.status_code}"
    assert "expenses" in resp_exp.context, "expenses missing in context"
    assert "total_expenses" in resp_exp.context, "total_expenses missing in context"
    print(f"✓ expenses_view GET: PASSED (Total Expenses: {resp_exp.context['total_expenses']} AFN)")

    # Post new expense
    exp_data = {
        "category": "قرطاسیه، چاپ و مواد درسی",
        "title": "خرید کتابچه و خودکار تست",
        "amount": "3200",
        "payment_date": "2024-10-18",
        "recipient": "فروشگاه تست",
        "receipt_number": "EXP-TEST-8888",
        "payment_method": "نقدی",
        "year_id": year.id,
        "month_id": month.id,
        "notes": "سند تستی",
    }
    resp_exp_post = client.post(url_exp, exp_data)
    assert resp_exp_post.status_code == 302, f"Expected 302 on expense post, got {resp_exp_post.status_code}"

    created_exp = Expense.objects.filter(receipt_number="EXP-TEST-8888").first()
    assert created_exp is not None, "Expense was not created in DB"
    assert created_exp.amount == 3200, "Expense amount mismatch"
    print(f"✓ expenses_view POST: PASSED (Created Expense ID {created_exp.id})")

    # 9. Test Financial Report View
    url_report = reverse("dashboard:finance-report")
    resp_report = client.get(url_report)
    assert resp_report.status_code == 200, f"Expected 200 on finance-report, got {resp_report.status_code}"
    assert "report" in resp_report.context, "report missing in context"
    report = resp_report.context["report"]
    assert "total_revenue_collected" in report
    assert "total_expenses" in report
    assert "net_operating_balance" in report
    print(f"✓ finance_report_view: PASSED (Revenues: {report['total_revenue_collected']}, Expenses: {report['total_expenses']}, Net: {report['net_operating_balance']})")

    # 10. Clean up test records
    url_fee_del = reverse("dashboard:fee-delete", kwargs={"id": created_fee.id})
    resp_fee_del = client.post(url_fee_del)
    assert resp_fee_del.status_code == 302
    assert not Fee.objects.filter(id=created_fee.id).exists(), "Fee was not deleted"
    print("✓ fee_delete: PASSED")

    url_exp_del = reverse("dashboard:expense-delete", kwargs={"id": created_exp.id})
    resp_exp_del = client.post(url_exp_del)
    assert resp_exp_del.status_code == 302
    assert not Expense.objects.filter(id=created_exp.id).exists(), "Expense was not deleted"
    print("✓ expense_delete: PASSED")

    print("\n=======================================================")
    print("★ ALL 10 FINANCE TESTS PASSED PERFECTLY! ★")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
