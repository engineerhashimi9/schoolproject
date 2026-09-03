from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView,DetailView
from .models import Student,Teacher
from django.contrib.auth import logout
# Create your views here.


def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return redirect(reverse("accounts:login"))

    return wrapper


@is_admin
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")
def custom_logout(request):
    logout(request)
    return redirect(reverse("accounts:login"))
class StudentListView(ListView):
    model = Student
    template_name = "dashboard/student_list.html"
    context_object_name="students"
class StudentDetailView(DetailView):
    model = Student
    template_name = "dashboard/student_detail.html"
    context_object_name="student"
    
class TeacherListView(ListView):
    model = Teacher
    template_name = "dashboard/workers_list.html"
    context_object_name="workers"
class TeacherDetailView(DetailView):
    model = Teacher
    template_name = "dashboard/worker_detail.html"
    context_object_name="worker"