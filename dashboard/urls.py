from django.urls import path
from . import views
app_name="dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="admin-dashboard"),
    path("studnet/", views.StudentListView.as_view(), name="student-list"),
    
]