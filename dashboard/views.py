from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import Student, Teacher, Classes, Job, StudentClass, AcademiceYear, Degree
from .forms import StudentForm, TeacherForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
import jdatetime
from django.db.models import Q


# Create your views here.

# is Admin derator
def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            return redirect(reverse("accounts:login"))

    return wrapper

# dashboard section


@is_admin
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")


############## ---------- STUDENT SECTION -------------------##
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "dashboard/student_list.html"
    context_object_name = "students"


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "dashboard/student_detail.html"
    context_object_name = "student"


@is_admin
def disable_student(request, id):
    target = get_object_or_404(Student, id=id)
    target.detached_date = jdatetime.date.today()
    target.status_id = 2
    target.save()
    return redirect(reverse("dashboard:student-list"))


@is_admin
def student_edite(request, id):
    student = get_object_or_404(Student, id=id)
    classes = Classes.objects.all()
    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            if student.school_id != form.cleaned_data["school_id"]:
                student.school_id = form.cleaned_data["school_id"]
            if student.card_id != form.cleaned_data["card_id"]:
                student.card_id = form.cleaned_data["card_id"]
            if student.name != form.cleaned_data["name"]:
                student.name = form.cleaned_data["name"]
            if student.fname != form.cleaned_data["fname"]:
                student.fname = form.cleaned_data["fname"]
            if student.gfname != form.cleaned_data["gfname"]:
                student.gfname = form.cleaned_data["gfname"]
            if student.birth_date != form.cleaned_data["birth_date"]:
                student.birth_date = form.cleaned_data["birth_date"]
            if student.nationality != form.cleaned_data["nationality"]:
                student.nationality = form.cleaned_data["nationality"]
            if student.father_job.name != form.cleaned_data["father_job"]:
                fjob = Job.objects.get_or_create(
                    name=form.cleaned_data["father_job"])[0]
                student.father_job = fjob
            if student.phone != form.cleaned_data["phone"]:
                student.phone = form.cleaned_data["phone"]
            if student.mother_language.id != int(form.cleaned_data["mother_language"]):
                student.mother_language_id = int(
                    form.cleaned_data["mother_language"])
            if student.status.id != int(form.cleaned_data["status"]):
                student.status_id = int(form.cleaned_data["status"])
            if student.registered_date != form.cleaned_data["registered_date"]:
                student.registered_date = form.cleaned_data["registered_date"]
            if student.now_province.id != int(form.cleaned_data["now_province"]):
                student.now_province_id = int(
                    form.cleaned_data["now_province"])
            if student.now_district.id != int(form.cleaned_data["now_district"]):
                student.now_district_id = int(
                    form.cleaned_data["now_district"])
            if student.now_zone != int(form.cleaned_data["now_zone"]):
                student.now_zone = int(form.cleaned_data["now_zone"])
            if student.now_village != form.cleaned_data["now_village"]:
                student.now_village = form.cleaned_data["now_village"]
            if student.original_province.id != int(form.cleaned_data["original_province"]):
                student.original_province_id = int(
                    form.cleaned_data["original_province"])
            if student.original_district.id != int(form.cleaned_data["original_district"]):
                student.original_district_id = int(
                    form.cleaned_data["original_district"])
            if student.original_zone != int(form.cleaned_data["original_zone"]):
                student.original_zone = int(form.cleaned_data["original_zone"])
            if student.original_village != form.cleaned_data["original_village"]:
                student.original_village = form.cleaned_data["original_village"]
            student.save()

            if "class_section" in form.cleaned_data:
                grade, section = form.cleaned_data["class_section"].split("-")
                academice_year = int(form.cleaned_data["academice_year"])
                academice_year_obj = AcademiceYear.objects.filter(
                    year=academice_year).first()
                class_obj = get_object_or_404(
                    Classes, grade=grade, section=section, academice_year=academice_year_obj)
                student_class = StudentClass.objects.filter(
                    student=student).first()
                if student_class:
                    student_class.classs = class_obj
                    student_class.academice_year = academice_year_obj
                    student_class.save()
                else:
                    StudentClass.objects.create(
                        student=student, classs=class_obj, academice_year=academice_year_obj)
        else:
            print("form is not valid")
            print(form.errors)
        return redirect(reverse("dashboard:student-detail", kwargs={"pk": student.id}))
    else:
        return render(request, "dashboard/student_edite.html", {"student": student, "classes": classes})


@is_admin
def student_create(request):
    classes = Classes.objects.all()
    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            school_id = form.cleaned_data["school_id"]
            card_id = form.cleaned_data["card_id"]
            name = form.cleaned_data["name"]
            fname = form.cleaned_data["fname"]
            gfname = form.cleaned_data["gfname"]
            birth_date = form.cleaned_data["birth_date"]
            nationality = form.cleaned_data["nationality"]
            father_job = Job.objects.get_or_create(
                name=form.cleaned_data["father_job"])[0]
            phone = form.cleaned_data["phone"]
            mother_language = int(form.cleaned_data["mother_language"])
            status = int(form.cleaned_data["status"])
            registered_date = form.cleaned_data["registered_date"]
            grade, section = form.cleaned_data["class_section"].split("-")
            now_province = int(form.cleaned_data["now_province"])
            now_district = int(form.cleaned_data["now_district"])
            now_zone = int(form.cleaned_data["now_zone"])
            now_village = form.cleaned_data["now_village"]
            original_province = int(form.cleaned_data["original_province"])
            original_district = int(form.cleaned_data["original_district"])
            original_zone = int(form.cleaned_data["original_zone"])
            original_village = form.cleaned_data["original_village"]
            academice_year = int(form.cleaned_data["academice_year"])
            new_student = Student.objects.create(
                school_id=school_id,
                card_id=card_id,
                name=name,
                fname=fname,
                gfname=gfname,
                birth_date=birth_date,
                nationality=nationality,
                father_job=father_job,
                phone=phone,
                mother_language_id=mother_language,
                status_id=status,
                registered_date=registered_date,
                now_province_id=now_province,
                now_district_id=now_district,
                now_zone=now_zone,
                now_village=now_village,
                original_province_id=original_province,
                original_district_id=original_district,
                original_zone=original_zone,
                original_village=original_village
            )
            # academice_year_obj = get_object_or_404(AcademiceYear, year=academice_year)
            academice_year_obj = AcademiceYear.objects.filter(
                year=academice_year).first()
            class_obj = get_object_or_404(
                Classes, grade=grade, section=section, academice_year=academice_year_obj)

            StudentClass.objects.create(
                student=new_student, classs=class_obj, academice_year=academice_year_obj)
            return redirect(reverse("dashboard:student-list"))
        else:
            print(form.errors)

    return render(request, "dashboard/student_edite.html", {"classes": classes})

######### -------------- TEACHERS ANS WORKERS SECTION --------------###


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
    teacher = get_object_or_404(Teacher, id=id)
    classes = Classes.objects.filter(
        Q(guidence=teacher) | Q(guidence__isnull=True))
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            if teacher.name != form.cleaned_data["name"]:
                teacher.name = form.cleaned_data["name"]
            if teacher.fname != form.cleaned_data["fname"]:
                teacher.fname = form.cleaned_data["fname"]
            if teacher.last_name != form.cleaned_data["last_name"]:
                teacher.last_name = form.cleaned_data["last_name"]
            if teacher.phone != form.cleaned_data["phone"]:
                teacher.phone = form.cleaned_data["phone"]
            if teacher.major != form.cleaned_data["major"]:
                teacher.major = form.cleaned_data["major"]
            if teacher.degree.name != form.cleaned_data["degree"]:
                degree = Degree.objects.get_or_create(
                    name=form.cleaned_data["degree"])[0]
                teacher.degree = degree
            if teacher.job.name != form.cleaned_data["job"]:
                job = Job.objects.get_or_create(
                    name=form.cleaned_data["job"])[0]
                teacher.job = job
            if teacher.years_of_service != form.cleaned_data["years_of_service"]:
                teacher.years_of_service = form.cleaned_data["years_of_service"]
            if teacher.registered_date != form.cleaned_data["registered_date"]:
                teacher.registered_date = form.cleaned_data["registered_date"]
            if teacher.detached_date != form.cleaned_data["detached_date"]:
                teacher.detached_date = form.cleaned_data["detached_date"]
            if teacher.graduation_year != form.cleaned_data["graduation_year"]:
                teacher.graduation_year = form.cleaned_data["graduation_year"]
            if teacher.salary != form.cleaned_data["salary"]:
                teacher.salary = form.cleaned_data["salary"]
            if teacher.tax != form.cleaned_data["tax"]:
                teacher.tax = form.cleaned_data["tax"]
            if teacher.status.id != int(form.cleaned_data["status"]):
                teacher.status_id = int(form.cleaned_data["status"])
            teacher.save()
            guidence_at = form.cleaned_data["guidence_at"]
            if guidence_at:
                grade, section = guidence_at.split("-")
                class_obj = get_object_or_404(
                    Classes, grade=int(grade), section=section)
                class_obj.guidence = teacher
                class_obj.save()
            return redirect(reverse("dashboard:worker-detail", kwargs={"pk": teacher.id}))
        else:
            print(form.errors)
            print(request.POST)

    else:
        return render(request, "dashboard/worker_edite.html", {"teacher": teacher,"classes":classes})
@is_admin
def disable_teacher(request,id) :
    target=get_object_or_404(Teacher,id=id)
    target.detached_date = jdatetime.date.today()
    target.status_id = 2
    target.save()
    return redirect(reverse("dashboard:worker-list"))
    


@is_admin
def teacher_create(request):
    classes = Classes.objects.filter(guidence__isnull=True)
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            fname = form.cleaned_data["fname"]
            last_name = form.cleaned_data["last_name"]
            phone = form.cleaned_data["phone"]
            major = form.cleaned_data["major"]
            degree = Degree.objects.get_or_create(
                name=form.cleaned_data["degree"])[0]
            job = Job.objects.get_or_create(name=form.cleaned_data["job"])[0]
            years_of_service = form.cleaned_data["years_of_service"]
            registered_date = form.cleaned_data["registered_date"]
            detached_date = form.cleaned_data["detached_date"]
            graduation_year = form.cleaned_data["graduation_year"]
            salary = form.cleaned_data["salary"]
            tax = form.cleaned_data["tax"]
            status = int(form.cleaned_data["status"])
            new_teacher = Teacher.objects.create(
                name=name,
                fname=fname,
                last_name=last_name,
                phone=phone,
                major=major,
                degree=degree,
                job=job,
                years_of_service=years_of_service,
                registered_date=registered_date,
                detached_date=detached_date,
                graduation_year=graduation_year,
                salary=salary,
                tax=tax,
                status_id=status
            )
            guidence_at = form.cleaned_data["guidence_at"]
            if guidence_at:
                grade, section = guidence_at.split("-")

                class_obj = get_object_or_404(
                    Classes, grade=int(grade), section=section)
                class_obj.guidence = new_teacher
                class_obj.save()

            return redirect(reverse("dashboard:worker-list"))
        else:
            print(form.errors)
            print(request.POST)
    else:
        return render(request, "dashboard/worker_edite.html", {"classes": classes})


class ClassesListView(LoginRequiredMixin, ListView):
    model = Classes
    template_name = "dashboard/class_list.html"
    context_object_name = "classes"
