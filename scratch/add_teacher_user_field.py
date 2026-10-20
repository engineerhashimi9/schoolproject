import os

models_path = os.path.join("dashboard", "models.py")

with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add settings import if not present
if "from django.conf import settings" not in content:
    content = "from django.conf import settings\n" + content
    print("Added settings import")

# 2. Add user field to Teacher model
target = """class Teacher(models.Model):
    id = models.AutoField(primary_key=True)"""

replacement = """class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
        verbose_name="حساب کاربری ورود"
    )
    id = models.AutoField(primary_key=True)"""

normalized_content = content.replace("\r\n", "\n")
normalized_target = target.replace("\r\n", "\n")
normalized_replacement = replacement.replace("\r\n", "\n")

if normalized_target in normalized_content:
    updated = normalized_content.replace(normalized_target, normalized_replacement, 1)
    with open(models_path, "w", encoding="utf-8") as f:
        f.write(updated)
    print("SUCCESS: Added user OneToOneField to Teacher model.")
else:
    print("ERROR: Target not found in models.py")
