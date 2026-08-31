from django.urls import path
from . import views
app_name="dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="admin-dashboard"),
    path("student/", views.StudentListView.as_view(), name="student-list"),
    path("student/<int:pk>", views.StudentDetailView.as_view(), name="student-detail"),
    
]