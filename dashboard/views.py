from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from .models import Student
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

class StudentListView(ListView):
    model = Student
    template_name = "dashboard/student_list.html"
    context_object_name="students"
