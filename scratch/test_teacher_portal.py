import os
import sys
import django

# Set utf-8 output encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from dashboard.models import (
    Teacher, Classes, Subject, AcademiceYear, Month, Student, StudentClass,
    Attendance, Assessment, ExamMark
)

User = get_user_model()
client = Client()

print("=" * 60)
print("TESTING TEACHER PORTAL & MANAGEMENT MODULE")
print("=" * 60)

# 1. Test unauthenticated access
print("\n[Test 1] Unauthenticated access redirects to login:")
resp = client.get(reverse("dashboard:teacher-portal"))
assert resp.status_code == 302 and resp.url == reverse("accounts:login"), f"Expected 302 to login ({reverse('accounts:login')}), got {resp.status_code} to {resp.url}"
print(f"✓ Correctly redirected to login page ({resp.url}).")

# 2. Authenticate as Teacher
teacher_user = User.objects.filter(email="teacher@school.af").first()
assert teacher_user is not None, "Teacher user not found!"
login_ok = client.login(email="teacher@school.af", password="teacherpassword123")
assert login_ok, "Login failed for teacher@school.af"
print(f"\n[Test 2] Logged in as Teacher: {teacher_user.email} (Teacher ID: {teacher_user.teacher_profile.id} - {teacher_user.teacher_profile.name})")

# Test Teacher Portal Dashboard
resp = client.get(reverse("dashboard:teacher-portal"))
assert resp.status_code == 200, f"Portal returned {resp.status_code}"
assert "کارتابل" in resp.content.decode("utf-8"), "Persian text missing in portal response"
print("✓ Teacher Portal GET 200 OK with correct Persian context & KPIs.")

# Test Teacher Attendance GET
resp = client.get(reverse("dashboard:teacher-attendance"))
assert resp.status_code == 200, f"Attendance returned {resp.status_code}"
print("✓ Teacher Attendance GET 200 OK.")

# Test Teacher Attendance POST
target_class = Classes.objects.filter(guidence=teacher_user.teacher_profile).first()
if not target_class:
    target_class = Classes.objects.first()

target_month = Month.objects.first()
academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
enrollments = StudentClass.objects.filter(classs=target_class, academice_year=academic_year).select_related("student")
assert enrollments.exists(), f"No enrollments in class {target_class}"

first_std = enrollments.first().student

post_data = {
    "class_id": target_class.id,
    "month_id": target_month.id,
    "all_days": 24,
    f"present_{first_std.id}": 22,
    f"absent_{first_std.id}": 1,
    f"sick_{first_std.id}": 1,
    f"excused_{first_std.id}": 0,
}
resp = client.post(reverse("dashboard:teacher-attendance"), data=post_data, follow=True)
assert resp.status_code == 200, f"Attendance POST failed with {resp.status_code}"

att_record = Attendance.objects.filter(
    student=first_std, classs=target_class, month=target_month, academice_year=academic_year
).first()
assert att_record is not None, "Attendance record was not saved in DB!"
assert att_record.present == 22 and att_record.alldays == 24
print(f"✓ Teacher Attendance POST saved successfully! Student {first_std.name}: Present={att_record.present}/{att_record.alldays} ({att_record.get_present_percentage()}%)")

# Test Teacher Assessment GET & POST
resp = client.get(reverse("dashboard:teacher-assessment"))
assert resp.status_code == 200, f"Assessment GET returned {resp.status_code}"
print("✓ Teacher Assessment GET 200 OK.")

# Find an assigned subject
target_subject = Subject.objects.filter(classes=target_class).first() or Subject.objects.first()
post_data_ass = {
    "class_id": target_class.id,
    "subject_id": target_subject.id,
    "month_id": target_month.id,
    f"score_{first_std.id}": 88,
    f"max_{first_std.id}": 100,
}
resp = client.post(reverse("dashboard:teacher-assessment"), data=post_data_ass, follow=True)
assert resp.status_code == 200, f"Assessment POST returned {resp.status_code}"

ass_record = Assessment.objects.filter(
    student=first_std, classs=target_class, subject=target_subject, month=target_month, academice_year=academic_year
).first()
assert ass_record is not None, "Assessment record not saved in DB!"
assert ass_record.score == 88
print(f"✓ Teacher Assessment POST saved successfully! Student {first_std.name}: Score={ass_record.score}/{ass_record.max_score}")

# Test Teacher Shaqqa GET & POST
resp = client.get(f"{reverse('dashboard:teacher-shaqqa')}?class_id={target_class.id}&subject_id={target_subject.id}")
assert resp.status_code == 200, f"Shaqqa GET returned {resp.status_code}"
print("✓ Teacher Shaqqa GET 200 OK.")

post_data_shaqqa = {
    "class_id": target_class.id,
    "subject_id": target_subject.id,
    f"midterm_{first_std.id}": "35.5",
    f"final_{first_std.id}": "52.0",
    f"remarks_{first_std.id}": "بسیار عالی و کوشا",
}
resp = client.post(reverse("dashboard:teacher-shaqqa"), data=post_data_shaqqa, follow=True)
assert resp.status_code == 200, f"Shaqqa POST returned {resp.status_code}"

exam_mark = ExamMark.objects.filter(
    student=first_std, classs=target_class, subject=target_subject, academice_year=academic_year
).first()
assert exam_mark is not None, "ExamMark record not saved!"
assert float(exam_mark.midterm_marks) == 35.5
assert float(exam_mark.final_marks) == 52.0
assert float(exam_mark.total_marks) == 87.5
assert exam_mark.is_passed is True
print(f"✓ Teacher Shaqqa POST saved! MoE calculation: Midterm={exam_mark.midterm_marks} + Final={exam_mark.final_marks} = Total {exam_mark.total_marks} (Passed={exam_mark.is_passed})")

# Test Teacher Timetables & Students
resp = client.get(reverse("dashboard:teacher-my-timetable"))
assert resp.status_code == 200, f"My Timetable returned {resp.status_code}"
print("✓ Teacher My Timetable GET 200 OK.")

resp = client.get(reverse("dashboard:teacher-class-timetable"))
assert resp.status_code == 200, f"Class Timetable returned {resp.status_code}"
print("✓ Teacher Class Timetable GET 200 OK.")

resp = client.get(reverse("dashboard:teacher-students"))
assert resp.status_code == 200, f"Students returned {resp.status_code}"
print("✓ Teacher Students Roster GET 200 OK.")

# 3. Test Admin Switcher Access
client.logout()
admin_user = User.objects.filter(is_staff=True).first()
assert admin_user is not None
client.force_login(admin_user)
print(f"\n[Test 3] Logged in as Admin: {admin_user.email} (Staff={admin_user.is_staff})")

resp = client.get(reverse("dashboard:teacher-portal"))
assert resp.status_code == 200, f"Admin portal access returned {resp.status_code}"
print("✓ Administrator can access teacher portal.")

# Switch to another teacher
another_teacher = Teacher.objects.filter(status_id=1).exclude(id=teacher_user.teacher_profile.id).first()
if another_teacher:
    resp = client.get(f"{reverse('dashboard:teacher-portal')}?teacher_id={another_teacher.id}")
    assert resp.status_code == 200
    assert another_teacher.name in resp.content.decode("utf-8")
    print(f"✓ Admin switcher successfully switched to teacher {another_teacher.name} {another_teacher.last_name}.")

print("\n" + "=" * 60)
print("ALL TEACHER PORTAL TESTS PASSED FLAWLESSLY (100% SUCCESS)!")
print("=" * 60)
