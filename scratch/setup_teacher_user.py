import os
import sys
import django

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from dashboard.models import Teacher

User = get_user_model()

# Find teacher Zabihullah Barakzai
teacher_zabih = Teacher.objects.filter(name__icontains="ذبیح").first()
if not teacher_zabih:
    teacher_zabih = Teacher.objects.first()

teacher_user, created = User.objects.get_or_create(
    email="teacher@school.af",
    defaults={
        "name": teacher_zabih.name,
        "last_name": teacher_zabih.last_name,
        "is_staff": False,
        "is_active": True,
        "is_verified": True,
    }
)
if created:
    teacher_user.set_password("teacherpassword123")
    teacher_user.save()
    print("Created teacher user: teacher@school.af / teacherpassword123")
else:
    print("User teacher@school.af already exists")

teacher_zabih.user = teacher_user
teacher_zabih.save()
print(f"Linked user {teacher_user.email} to teacher: {teacher_zabih.name} {teacher_zabih.last_name}")
