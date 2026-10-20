import os

urls_path = os.path.join("dashboard", "urls.py")

with open(urls_path, "r", encoding="utf-8") as f:
    content = f.read()

target = "    path(\"timetable/teacher/<int:teacher_id>/print/\", views.timetable_teacher_print, name=\"timetable-teacher-print\"),"

new_urls = """    path("timetable/teacher/<int:teacher_id>/print/", views.timetable_teacher_print, name="timetable-teacher-print"),
    # Subject & Afghan Curriculum Management URLs (مدیریت مضامین و نصاب تعلیمی)
    path("subjects/", views.subject_list_view, name="subject-list"),
    path("subjects/create/", views.subject_create_view, name="subject-create"),
    path("subjects/<int:id>/", views.subject_detail_view, name="subject-detail"),
    path("subjects/<int:id>/edit/", views.subject_edit_view, name="subject-edit"),
    path("subjects/<int:id>/delete/", views.subject_delete_view, name="subject-delete"),
    path("subjects/<int:id>/toggle-status/", views.subject_toggle_status_view, name="subject-toggle-status"),
    path("subjects/class-matrix/", views.subject_class_matrix_view, name="subject-class-matrix"),
    path("subjects/class/<int:class_id>/print/", views.subject_class_print_view, name="subject-class-print"),"""

if target in content:
    content = content.replace(target, new_urls, 1)
    with open(urls_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Registered subject URLs in dashboard/urls.py")
else:
    print("ERROR: Target line not found in dashboard/urls.py")
