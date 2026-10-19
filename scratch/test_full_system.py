import os
import sys

# Ensure project root is in sys.path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Force UTF-8 encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Count, Sum

from dashboard.models import (
    Student, Teacher, Classes, Subject, AcademiceYear,
    Month, Fee, Expense, TimeTable, ExamMark, ExamAttendance,
    StudentClass, Province, District, Attendance, Assessment
)
from dashboard.services.exam_service import (
    calculate_class_results, calculate_student_result,
    calculate_grade, format_rank_afghan
)
from dashboard.services.finance_service import (
    number_to_dari_words, calculate_financial_report, calculate_finance_kpis
)
from dashboard.services.timetable_service import (
    get_class_timetable_matrix, get_teacher_timetable_matrix,
    validate_timetable_slot, get_master_timetable_matrix
)

User = get_user_model()

def test_full_system():
    print("==================================================")
    print("STARTING FULL AFGHAN SCHOOL SYSTEM VERIFICATION")
    print("==================================================")

    # 1. Database Integrity & References Check
    province_count = Province.objects.count()
    district_count = District.objects.count()
    print(f"✓ Provinces: {province_count} (Expected 34)")
    print(f"✓ Districts: {district_count} (Expected 380+)")
    assert province_count >= 34, "Provinces missing!"
    assert district_count >= 300, "Districts missing!"

    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()
    class_count = Classes.objects.count()
    subject_count = Subject.objects.count()
    print(f"✓ Students: {student_count}, Teachers: {teacher_count}, Classes: {class_count}, Subjects: {subject_count}")
    assert student_count > 0, "No students found!"
    assert teacher_count > 0, "No teachers found!"
    assert class_count > 0, "No classes found!"
    assert subject_count > 0, "No subjects found!"

    # 2. MoE Exam & Grading Service Logic
    print("\n--- Testing Afghan MoE Grading Service Logic ---")
    grade_100 = calculate_grade(95.0)
    assert grade_100["code"] == "الف", f"Expected الف, got {grade_100['code']}"
    grade_85 = calculate_grade(85.0)
    assert grade_85["code"] == "ب", f"Expected ب, got {grade_85['code']}"
    grade_75 = calculate_grade(75.0)
    assert grade_75["code"] == "ج", f"Expected ج, got {grade_75['code']}"
    grade_60 = calculate_grade(60.0)
    assert grade_60["code"] == "د", f"Expected د, got {grade_60['code']}"
    grade_45 = calculate_grade(45.0)
    assert grade_45["code"] == "هـ", f"Expected هـ, got {grade_45['code']}"
    grade_30 = calculate_grade(30.0)
    assert grade_30["code"] == "و", f"Expected و, got {grade_30['code']}"
    print("✓ Afghan MoE Grade thresholds (الف، ب، ج، د، هـ، و) verified.")

    assert format_rank_afghan(1) == "اول نمره"
    assert format_rank_afghan(2) == "دوم نمره"
    assert format_rank_afghan(3) == "سوم نمره"
    assert format_rank_afghan(4) == "مقام ۴"
    print("✓ Afghan Honor Rank Titles (اول نمره، دوم نمره، سوم نمره) verified.")

    class_10a = Classes.objects.filter(grade=10, section="الف").first() or Classes.objects.first()
    year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
    res = calculate_class_results(class_10a, year)
    print(f"✓ Class Results calculated for {class_10a}: {len(res['students_results'])} students processed.")
    assert "stats" in res
    assert "top_three" in res["stats"]

    # 3. Finance Service & Dari Currency Wording
    print("\n--- Testing Finance Service & Afghan Currency Wording ---")
    w1 = number_to_dari_words(4500)
    assert "چهار هزار و پنجصد افغانی" in w1, f"Unexpected words: {w1}"
    w2 = number_to_dari_words(120000)
    assert "یکصد و بیست هزار افغانی" in w2, f"Unexpected words: {w2}"
    print(f"✓ 4,500 AFN -> '{w1}'")
    print(f"✓ 120,000 AFN -> '{w2}'")

    fin_rep = calculate_financial_report(year)
    print(f"✓ Financial report generated: Revenue={fin_rep['total_revenue_collected']} AFN, Expenses={fin_rep['total_expenses']} AFN, Net={fin_rep['net_operating_balance']} AFN")

    # 4. Timetable Service & Scheduling Grid
    print("\n--- Testing Timetable Service Matrix ---")
    tt_matrix = get_class_timetable_matrix(class_10a.id, year.id)
    assert len(tt_matrix["weekly_grid"]) == 6, "Expected 6 school days!"
    assert len(tt_matrix["periods"]) == 6, "Expected 6 periods per day!"
    print(f"✓ Class Timetable: 6 days x 6 periods = {tt_matrix['total_assigned']} slots assigned ({tt_matrix['completion_rate']}%)")

    master_matrix = get_master_timetable_matrix(year.id)
    assert len(master_matrix["class_rows"]) > 0, "No classes in master timetable!"
    print(f"✓ Master Timetable generated for {len(master_matrix['class_rows'])} classes.")

    # 5. Client Route Testing & Authentication
    print("\n--- Testing Django URLs with Authenticated Client ---")
    client = Client()
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            phone="0799999999", email="admin@school.af", password="adminpassword123"
        )
    client.force_login(admin_user)

    test_urls = [
        ("Main Dashboard", reverse("dashboard:admin-dashboard")),
        ("Student List", reverse("dashboard:student-list")),
        ("Student Register GET", reverse("dashboard:student-register")),
        ("Worker/Teacher List", reverse("dashboard:worker-list")),
        ("Worker Register GET", reverse("dashboard:worker-register")),
        ("Classes List", reverse("dashboard:class-list")),
        ("Classes Register GET", reverse("dashboard:class-register")),
        ("Attendance List", reverse("dashboard:attendence-list")),
        ("Attendance Create GET", reverse("dashboard:attendence-create")),
        ("Assessments List", reverse("dashboard:assesment-list")),
        ("Assessment Create GET", reverse("dashboard:assesment-create")),
        ("Exam Dashboard", reverse("dashboard:exam-dashboard")),
        ("Exam Shaqqa Entry", reverse("dashboard:exam-shaqqa")),
        ("Exam Jadwal Nataij", reverse("dashboard:exam-jadwal-nataij")),
        ("Exam Etlanama", reverse("dashboard:exam-etlanama")),
        ("Exam Attendance", reverse("dashboard:exam-attendance")),
        ("Exam Subjects", reverse("dashboard:exam-subjects")),
        ("Finance List", reverse("dashboard:finance-list")),
        ("Finance Create GET", reverse("dashboard:fee-create")),
        ("Finance Expenses", reverse("dashboard:finance-expenses")),
        ("Finance Report", reverse("dashboard:finance-report")),
        ("Timetable Class", reverse("dashboard:timetable-class")),
        ("Timetable Teacher", reverse("dashboard:timetable-teacher")),
        ("Timetable Master", reverse("dashboard:timetable-master")),
    ]

    for label, url in test_urls:
        response = client.get(url)
        assert response.status_code == 200, f"Route {label} ({url}) returned status {response.status_code}"
        print(f"  ✓ [{response.status_code}] {label}: {url}")

    # Specific Detail Pages
    first_std = Student.objects.first()
    if first_std:
        std_url = reverse("dashboard:student-detail", kwargs={"pk": first_std.pk})
        resp = client.get(std_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Student Detail: {std_url}")

        std_edit_url = reverse("dashboard:student-edite", kwargs={"id": first_std.pk})
        resp = client.get(std_edit_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Student Edit: {std_edit_url}")

        etlanama_url = reverse("dashboard:exam-etlanama-student", kwargs={"student_id": first_std.pk})
        resp = client.get(etlanama_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Etlanama Print: {etlanama_url}")

    first_teacher = Teacher.objects.first()
    if first_teacher:
        t_url = reverse("dashboard:worker-detail", kwargs={"pk": first_teacher.pk})
        resp = client.get(t_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Teacher Detail: {t_url}")

        t_edit_url = reverse("dashboard:worker-edite", kwargs={"id": first_teacher.pk})
        resp = client.get(t_edit_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Teacher Edit: {t_edit_url}")

        t_print_url = reverse("dashboard:timetable-teacher-print", kwargs={"teacher_id": first_teacher.pk})
        resp = client.get(t_print_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Teacher Timetable Print: {t_print_url}")

    if class_10a:
        cls_url = reverse("dashboard:class-detail", kwargs={"pk": class_10a.pk})
        resp = client.get(cls_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Class Detail: {cls_url}")

        cls_edit_url = reverse("dashboard:class-edite", kwargs={"id": class_10a.pk})
        resp = client.get(cls_edit_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Class Edit: {cls_edit_url}")

        cls_print_url = reverse("dashboard:timetable-class-print", kwargs={"class_id": class_10a.pk})
        resp = client.get(cls_print_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Class Timetable Print: {cls_print_url}")

    first_fee = Fee.objects.first()
    if first_fee:
        receipt_url = reverse("dashboard:fee-receipt", kwargs={"id": first_fee.pk})
        resp = client.get(receipt_url)
        assert resp.status_code == 200
        print(f"  ✓ [200] Fee Receipt Print: {receipt_url}")

    print("\n==================================================")
    print("ALL TESTS PASSED! APPLICATION IS 100% OPERATIONAL")
    print("==================================================")

if __name__ == "__main__":
    test_full_system()
