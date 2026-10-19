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
from dashboard.models import Classes, Teacher, Subject, AcademiceYear, TimeTable
from dashboard.services.timetable_service import (
    get_class_timetable_matrix,
    get_teacher_timetable_matrix,
    get_master_timetable_matrix,
    validate_timetable_slot,
    DAYS,
    PERIODS,
)

User = get_user_model()

def run_tests():
    print("=== STARTING TIMETABLE MODULE AUTOMATED TESTS ===")

    year1403 = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
    cls = Classes.objects.filter(alpha_grade="دهم", section="الف").first() or Classes.objects.first()
    teacher = Teacher.objects.filter(status__id=1).first()

    # 1. Test Matrix Service
    class_matrix = get_class_timetable_matrix(cls.id, year1403.id)
    assert len(class_matrix["weekly_grid"]) == 6, "Expected 6 days in grid"
    assert len(class_matrix["periods"]) == 6, "Expected 6 periods"
    assert class_matrix["total_assigned"] > 0, "Expected assigned slots in Class 10-A"
    print(f"✓ get_class_timetable_matrix: PASSED ({class_matrix['total_assigned']} slots, {class_matrix['completion_rate']}% complete)")

    teacher_matrix = get_teacher_timetable_matrix(teacher.id, year1403.id)
    assert len(teacher_matrix["weekly_grid"]) == 6
    assert teacher_matrix["total_teaching_hours"] >= 0
    print(f"✓ get_teacher_timetable_matrix: PASSED ({teacher_matrix['total_teaching_hours']} teaching hours)")

    master_matrix = get_master_timetable_matrix(year1403.id, 1)
    assert len(master_matrix["class_rows"]) > 0
    print(f"✓ get_master_timetable_matrix: PASSED ({len(master_matrix['class_rows'])} classes on Saturday)")

    # 2. Test Conflict Validation
    # Pick an existing slot
    existing_slot = TimeTable.objects.filter(academic_year=year1403).first()
    assert existing_slot is not None, "Need existing slot to test conflicts"

    # Try to assign the same teacher to ANOTHER class at the same time
    other_class = Classes.objects.exclude(id=existing_slot.classs_id).first()
    if other_class:
        is_valid, msg = validate_timetable_slot(
            class_id=other_class.id,
            teacher_id=existing_slot.teacher_id,
            day_of_week=existing_slot.day_of_week,
            period=existing_slot.period,
            academic_year_id=year1403.id,
        )
        assert not is_valid, "Expected teacher conflict to fail validation!"
        assert "تداخل زمانی استاد" in msg, f"Expected teacher conflict message, got: {msg}"
        print("✓ Conflict Detection (Teacher Double-Booking): PASSED")

    # 3. Test HTTP Views via Client
    client = Client()
    admin_user = User.objects.filter(is_staff=True).first()
    client.force_login(admin_user)
    print(f"✓ Authenticated as admin: {admin_user.email}")

    # GET Class Timetable
    url_class = f"{reverse('dashboard:timetable-class')}?class_id={cls.id}&year_id={year1403.id}"
    resp = client.get(url_class)
    assert resp.status_code == 200, f"Expected 200 on timetable-class, got {resp.status_code}"
    assert "matrix" in resp.context
    assert "class_subjects" in resp.context
    print("✓ timetable_class_view GET: PASSED")

    # GET Teacher Timetable
    url_teacher = f"{reverse('dashboard:timetable-teacher')}?teacher_id={teacher.id}&year_id={year1403.id}"
    resp_t = client.get(url_teacher)
    assert resp_t.status_code == 200, f"Expected 200 on timetable-teacher, got {resp_t.status_code}"
    print("✓ timetable_teacher_view GET: PASSED")

    # GET Master Timetable
    url_master = f"{reverse('dashboard:timetable-master')}?day=1&year_id={year1403.id}"
    resp_m = client.get(url_master)
    assert resp_m.status_code == 200, f"Expected 200 on timetable-master, got {resp_m.status_code}"
    print("✓ timetable_master_view GET: PASSED")

    # GET Printable Class Wall Timetable
    url_print_c = reverse("dashboard:timetable-class-print", kwargs={"class_id": cls.id})
    resp_pc = client.get(url_print_c)
    assert resp_pc.status_code == 200
    html_c = resp_pc.content.decode("utf-8")
    assert "جدول تقسیم اوقات رسمی دروس" in html_c
    print("✓ timetable_class_print GET: PASSED")

    # GET Printable Teacher Timetable
    url_print_t = reverse("dashboard:timetable-teacher-print", kwargs={"teacher_id": teacher.id})
    resp_pt = client.get(url_print_t)
    assert resp_pt.status_code == 200
    html_t = resp_pt.content.decode("utf-8")
    assert "کارت برنامه کاری و تقسیم اوقات استاد" in html_t
    print("✓ timetable_teacher_print GET: PASSED")

    # POST Save Slot
    subject = Subject.objects.first()
    save_url = reverse("dashboard:timetable-slot-save")
    # Slot with conflict
    if other_class:
        post_conflict = {
            "class_id": other_class.id,
            "teacher_id": existing_slot.teacher_id,
            "subject_id": subject.id,
            "day_of_week": existing_slot.day_of_week,
            "period": existing_slot.period,
            "year_id": year1403.id,
            "room_number": "اتاق تست",
            "redirect_to": "class",
        }
        resp_conf = client.post(save_url, post_conflict, follow=True)
        messages_text = [m.message for m in resp_conf.context["messages"]]
        assert any("تداخل" in m for m in messages_text), "Conflict error message should be displayed!"
        print("✓ timetable_slot_save conflict prevention: PASSED")

    # POST Save valid slot
    # Find a class and teacher who are genuinely free on Day 6, Period 6
    free_teacher = [
        t for t in Teacher.objects.filter(status__id=1)
        if not TimeTable.objects.filter(teacher=t, day_of_week=6, period=6, academic_year=year1403).exists()
    ][0]

    free_class = [
        c for c in Classes.objects.all()
        if not TimeTable.objects.filter(classs=c, day_of_week=6, period=6, academic_year=year1403).exists()
    ][0]

    post_valid = {
        "class_id": free_class.id,
        "teacher_id": free_teacher.id,
        "subject_id": subject.id,
        "day_of_week": "6", # پنجشنبه
        "period": "6",      # ساعت ششم
        "year_id": year1403.id,
        "room_number": "اتاق ۲۰۱",
        "notes": "ساعت تست",
        "redirect_to": "class",
    }
    resp_valid = client.post(save_url, post_valid)
    assert resp_valid.status_code == 302
    created_test_slot = TimeTable.objects.filter(
        classs=free_class,
        day_of_week=6,
        period=6,
        academic_year=year1403,
    ).first()
    assert created_test_slot is not None, "Valid slot was not saved!"
    print(f"✓ timetable_slot_save valid creation: PASSED (ID: {created_test_slot.id})")

    # Delete Slot
    del_url = reverse("dashboard:timetable-slot-delete", kwargs={"id": created_test_slot.id})
    resp_del = client.post(del_url)
    assert resp_del.status_code == 302
    assert not TimeTable.objects.filter(id=created_test_slot.id).exists(), "Slot was not deleted!"
    print("✓ timetable_slot_delete: PASSED")

    print("\n=======================================================")
    print("★ ALL TIMETABLE TESTS PASSED PERFECTLY! ★")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
