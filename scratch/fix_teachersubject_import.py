import os

views_path = os.path.join("dashboard", "views.py")

with open(views_path, "r", encoding="utf-8") as f:
    content = f.read()

target = "    ExamMark, ExamAttendance, Shaqqa, Expense, TimeTable"
replacement = "    ExamMark, ExamAttendance, Shaqqa, Expense, TimeTable, TeacherSubject"

if target in content:
    content = content.replace(target, replacement, 1)
    with open(views_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Added TeacherSubject to imports in dashboard/views.py")
else:
    print("ERROR: Target line not found")
