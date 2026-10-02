from django.urls import path
from . import views
app_name = "dashboard"

urlpatterns = [
    # main dashboard
    path("", views.dashboard_view, name="admin-dashboard"),

    # student urls
    path("student/", views.StudentListView.as_view(), name="student-list"),
    path("student/create", views.student_create, name="student-register"),
    path("student/<int:pk>", views.StudentDetailView.as_view(),
         name="student-detail"),
    path("student/<int:id>/disable", views.disable_student, name="student-disable"),
    path("student/<int:id>/edite", views.student_edite, name="student-edite"),

    # worker urls
    path("worker/", views.TeacherListView.as_view(), name="worker-list"),
    path("worker/create", views.teacher_create, name="worker-register"),
    path("worker/<int:pk>", views.TeacherDetailView.as_view(), name="worker-detail"),
    path("worker/<int:id>/edite", views.teacher_edite, name="worker-edite"),
    path("woreker/<int:id>/disable", views.disable_teacher, name="worker-disable"),

    # classes urls
    path("class/", views.ClassesListView.as_view(), name="class-list"),
    path("class/<int:pk>", views.ClassDetailView.as_view(), name="class-detail"),
    path("class/<int:id>/edite", views.class_edite, name="class-edite"),
    # attendence urls
    path("attendence/", views.AttendenceListView.as_view(
    ), name="attendence-list"),

    # assesment urls
    path("assesment/", views.AssesmentListView.as_view(
    ), name="assesment-list"),
    # exam urls
    path("exam/", views.ExamListView.as_view(
    ), name="exam-list"),
    # register urls
    # path("register/province", views.register_pro, name="register-province"),

]
