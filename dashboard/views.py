from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import Student, Teacher, Classes
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

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


@is_admin
def delete_student(request, id):
    target = get_object_or_404(Student, id=id)
    target.status_id = 2
    target.save()
    return redirect(reverse("dashboard:student-list"))


@is_admin
def edite_student(request, id):
    if request.method == "POST":
        print(request.POST)
        return redirect(reverse("dashboard:student-detail", kwargs={"pk": id}))
    else:
        student = get_object_or_404(Student, id=id)
        classes = Classes.objects.all()
        return render(request, "dashboard/student_edite.html", {"student": student, "classes": classes})


class StudentListView(ListView, LoginRequiredMixin):
    model = Student
    template_name = "dashboard/student_list.html"
    context_object_name = "students"


class StudentDetailView(DetailView, LoginRequiredMixin):
    model = Student
    template_name = "dashboard/student_detail.html"
    context_object_name = "student"


class TeacherListView(ListView, LoginRequiredMixin):
    model = Teacher
    template_name = "dashboard/workers_list.html"
    context_object_name = "workers"


class TeacherDetailView(DetailView, LoginRequiredMixin):
    model = Teacher
    template_name = "dashboard/worker_detail.html"
    context_object_name = "worker"
