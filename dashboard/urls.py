from django.urls import path
from . import views
app_name = "dashboard"

urlpatterns = [
    # main dashboard
    path("", views.dashboard_view, name="admin-dashboard"),

    # student urls
    path("student/", views.StudentListView.as_view(), name="student-list"),
    path("student/<int:pk>", views.StudentDetailView.as_view(),
         name="student-detail"),
    path("student/<int:id>/disable", views.delete_student, name="student-disable"),
    path("student/<int:id>/edite", views.student_edite, name="student-edite"),

    # worker urls
    path("worker/", views.TeacherListView.as_view(), name="worker-list"),
    path("worker/<int:pk>", views.TeacherDetailView.as_view(), name="worker-detail"),
    path("worker/<int:id>/edite", views.teacher_edite, name="worker-edite"),

    # classes urls
    path("class/", views.ClassesListView.as_view(), name="class-list"),

]
