from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.teacher_dashboard_view, name="dashboard"),
    path("attendance/", views.teacher_attendance_view, name="attendance"),
    path("assessment/", views.teacher_assessment_view, name="assessment"),
    path("shaqqa/", views.teacher_shaqqa_view, name="shaqqa"),
    path("timetable/my/", views.teacher_my_timetable_view, name="my-timetable"),
    path("timetable/class/", views.teacher_class_timetable_view, name="class-timetable"),
    path("students/", views.teacher_students_view, name="students"),
    path("profile/", views.teacher_profile_view, name="profile"),
]
