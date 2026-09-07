from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import Student, Teacher, Classes

from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
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
def student_edite(request, id):
    student = get_object_or_404(Student, id=id)
    classes = Classes.objects.all()
    if request.method == "POST":
        print(request.POST)
        return redirect(reverse("dashboard:student-detail", kwargs={"pk": id}))
    else:
        return render(request, "dashboard/student_edite.html", {"student": student, "classes": classes})


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "dashboard/student_list.html"
    context_object_name = "students"


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "dashboard/student_detail.html"
    context_object_name = "student"


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = "dashboard/workers_list.html"
    context_object_name = "workers"


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = "dashboard/worker_detail.html"
    context_object_name = "worker"


@is_admin
def teacher_edite(request, id):
    teachers = get_object_or_404(Teacher, id=id)
    if request.method == "POST":
        pass
    else:
        return render(request, "dashboard/worker_edite.html", {"teacher": teachers})


class ClassesListView(LoginRequiredMixin, ListView):
    model = Classes
    template_name = "dashboard/class_list.html"
    context_object_name = "classes"
