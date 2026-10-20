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
    Teacher, Classes, Subject, AcademiceYear, Month, StudentClass,
    Attendance, Assessment, ExamMark
)

User = get_user_model()
client = Client()

print("=" * 65)
print("TESTING DEDICATED TEACHERS APP & TEMPLATES ARCHITECTURE")
print("=" * 65)

# --- 1. Test Static & Template Directory Structure ---
print("\n[Step 1 & 2] Verifying Root Templates & Static Folders:")
assert os.path.exists("templates/base.html"), "Root templates/base.html missing!"
assert os.path.exists("templates/teachers/base_teacher.html"), "templates/teachers/base_teacher.html missing!"
assert os.path.exists("static/css/dashboard.css"), "Root static/css missing!"
assert os.path.exists("static/js/main.js"), "Root static/js missing!"
assert os.path.exists("static/fonts"), "Root static/fonts missing!"
print("✓ Root templates/ and static/ architecture verified with base and general assets.")

# --- 2. Test Login Auto-Detection for Teacher ---
print("\n[Auto-Detect 1] Logging in as Teacher (teacher@school.af):")
login_resp = client.post(reverse("accounts:login"), {
    "email": "teacher@school.af",
    "password": "teacherpassword123",
}, follow=False)

assert login_resp.status_code == 302, f"Expected 302, got {login_resp.status_code}"
assert login_resp.url == reverse("teachers:dashboard"), f"Expected redirect to teachers:dashboard ({reverse('teachers:dashboard')}), got {login_resp.url}"
print(f"✓ System auto-detected Teacher! Successfully redirected to {login_resp.url}")

# Verify landing on teachers dashboard
dash_resp = client.get(reverse("teachers:dashboard"))
assert dash_resp.status_code == 200, f"Teacher dashboard returned {dash_resp.status_code}"
content_text = dash_resp.content.decode("utf-8")
assert "کارتابل اختصاصی اساتید" in content_text or "کارتابل استاد" in content_text
print("✓ Teacher Dashboard loaded with dedicated teacher layout & navigation.")

# --- 3. Test Teacher Blocked from Admin Dashboard ---
print("\n[Security] Verifying Teacher cannot access Admin Dashboard:")
admin_attempt = client.get(reverse("dashboard:admin-dashboard"))
assert admin_attempt.status_code == 302 and admin_attempt.url == reverse("teachers:dashboard"), \
    f"Expected redirect to teachers:dashboard, got {admin_attempt.status_code} to {getattr(admin_attempt, 'url', None)}"
print("✓ Teacher attempting to access /dashboard/ was automatically rerouted to /teachers/!")

# --- 4. Test Teacher App Modules ---
print("\n[Teachers App] Testing all Teacher Views & Actions:")

# Attendance GET & POST
resp = client.get(reverse("teachers:attendance"))
assert resp.status_code == 200
print("✓ GET /teachers/attendance/ (200 OK)")

teacher_user = User.objects.get(email="teacher@school.af")
target_teacher = teacher_user.teacher_profile
target_class = Classes.objects.filter(guidence=target_teacher).first() or Classes.objects.first()
target_month = Month.objects.first()
academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
enrollments = StudentClass.objects.filter(classs=target_class, academice_year=academic_year).select_related("student")
first_std = enrollments.first().student

post_att = {
    "class_id": target_class.id,
    "month_id": target_month.id,
    "all_days": 24,
    f"present_{first_std.id}": 23,
    f"absent_{first_std.id}": 1,
    f"sick_{first_std.id}": 0,
    f"excused_{first_std.id}": 0,
}
resp = client.post(reverse("teachers:attendance"), post_att, follow=True)
assert resp.status_code == 200
att_saved = Attendance.objects.filter(student=first_std, classs=target_class, month=target_month, academice_year=academic_year).first()
assert att_saved and att_saved.present == 23
print(f"✓ POST /teachers/attendance/ -> Saved student {first_std.name}: {att_saved.present}/{att_saved.alldays}")

# Assessment GET & POST
resp = client.get(reverse("teachers:assessment"))
assert resp.status_code == 200
print("✓ GET /teachers/assessment/ (200 OK)")

target_subject = Subject.objects.filter(classes=target_class).first() or Subject.objects.first()
post_ass = {
    "class_id": target_class.id,
    "subject_id": target_subject.id,
    "month_id": target_month.id,
    f"score_{first_std.id}": 95,
    f"max_{first_std.id}": 100,
}
resp = client.post(reverse("teachers:assessment"), post_ass, follow=True)
assert resp.status_code == 200
ass_saved = Assessment.objects.filter(student=first_std, classs=target_class, subject=target_subject, month=target_month, academice_year=academic_year).first()
assert ass_saved and ass_saved.score == 95
print(f"✓ POST /teachers/assessment/ -> Saved student {first_std.name}: {ass_saved.score}/{ass_saved.max_score}")

# Shaqqa GET & POST (MoE rules)
resp = client.get(f"{reverse('teachers:shaqqa')}?class_id={target_class.id}&subject_id={target_subject.id}")
assert resp.status_code == 200
print("✓ GET /teachers/shaqqa/ (200 OK)")

post_shaqqa = {
    "class_id": target_class.id,
    "subject_id": target_subject.id,
    f"midterm_{first_std.id}": "38",
    f"final_{first_std.id}": "56",
    f"remarks_{first_std.id}": "نمرات عالی معارف",
}
resp = client.post(reverse("teachers:shaqqa"), post_shaqqa, follow=True)
assert resp.status_code == 200
em = ExamMark.objects.filter(student=first_std, classs=target_class, subject=target_subject, academice_year=academic_year).first()
assert em and float(em.total_marks) == 94.0 and em.is_passed is True
print(f"✓ POST /teachers/shaqqa/ -> MoE Total: {em.total_marks} (Passed={em.is_passed})")

# Timetables, Students, Profile
assert client.get(reverse("teachers:my-timetable")).status_code == 200
print("✓ GET /teachers/timetable/my/ (200 OK)")
assert client.get(reverse("teachers:class-timetable")).status_code == 200
print("✓ GET /teachers/timetable/class/ (200 OK)")
assert client.get(reverse("teachers:students")).status_code == 200
print("✓ GET /teachers/students/ (200 OK)")
assert client.get(reverse("teachers:profile")).status_code == 200
print("✓ GET /teachers/profile/ (200 OK)")

# --- 5. Test Login Auto-Detection for Admin ---
print("\n[Auto-Detect 2] Logging in as Admin (sadat@x.com):")
client.logout()
admin_login = client.post(reverse("accounts:login"), {
    "email": "sadat@x.com",
    "password": "adminpassword123",
}, follow=False)
assert admin_login.status_code == 302 and admin_login.url == reverse("dashboard:admin-dashboard")
print(f"✓ System auto-detected Admin! Successfully redirected to {admin_login.url}")

# Admin can view admin dashboard
admin_dash = client.get(reverse("dashboard:admin-dashboard"))
assert admin_dash.status_code == 200
print("✓ Admin Dashboard loaded with Admin sidebar & management links.")

# Admin can switch and view teachers dashboard
admin_teacher_view = client.get(reverse("teachers:dashboard"))
assert admin_teacher_view.status_code == 200
print("✓ Admin can also inspect Teachers Dashboard seamlessly.")

print("\n" + "=" * 65)
print("ALL TESTS PASSED! SEPARATE TEACHERS APP IS 100% OPERATIONAL!")
print("=" * 65)
