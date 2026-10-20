import re

with open("dashboard/urls.py", "r", encoding="utf-8") as f:
    content = f.read()

target = '    path("subjects/class/<int:class_id>/print/", views.subject_class_print_view, name="subject-class-print"),'
replacement = """    path("subjects/class/<int:class_id>/print/", views.subject_class_print_view, name="subject-class-print"),
    # Teacher Dashboard & Management URLs (پورتال و مدیریت اختصاصی اساتید)
    path("teacher/", views.teacher_portal_view, name="teacher-portal"),
    path("teacher/attendance/", views.teacher_attendance_view, name="teacher-attendance"),
    path("teacher/assessment/", views.teacher_assessment_view, name="teacher-assessment"),
    path("teacher/shaqqa/", views.teacher_shaqqa_view, name="teacher-shaqqa"),
    path("teacher/timetable/my/", views.teacher_my_timetable_view, name="teacher-my-timetable"),
    path("teacher/timetable/class/", views.teacher_class_timetable_view, name="teacher-class-timetable"),
    path("teacher/students/", views.teacher_students_view, name="teacher-students"),"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open("dashboard/urls.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Updated dashboard/urls.py")
else:
    print("ERROR: Target not found in dashboard/urls.py")
