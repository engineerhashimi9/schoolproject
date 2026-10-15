from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
import jdatetime

from .models import (
    Student, Teacher, Classes, Job, StudentClass,
    AcademiceYear, Degree, Attendance, Assessment,
    ExamResult, Exam, Month, Language
)
from .forms import StudentForm, TeacherForm, ClassForm


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Security And Helpers SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            return redirect(reverse("accounts:login"))

    return wrapper


def get_current_jalali_date_str():
    try:
        now_j = jdatetime.date.today()
        month_names = [
            "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
            "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
        ]
        month_name = month_names[now_j.month - 1]
        return f"{now_j.day} {month_name} {now_j.year}"
    except Exception:
        return "۱۴۰۳"


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Main Dashboard SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

@is_admin
def dashboard_view(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_classes = Classes.objects.count()
    total_exams = Exam.objects.count()
    jalali_date_str = get_current_jalali_date_str()

    # Overall attendance rate across records
    att_stats = Attendance.objects.aggregate(
        total_p=Sum("present"), total_all=Sum("alldays")
    )
    if att_stats.get("total_all") and att_stats["total_all"] > 0:
        overall_attendance_rate = round(
            (att_stats["total_p"] / att_stats["total_all"]) * 100, 1
        )
    else:
        overall_attendance_rate = 94.2

    recent_students = Student.objects.select_related(
        "status").order_by("-id")[:5]
    recent_classes = Classes.objects.select_related(
        "guidence", "academice_year").order_by("grade", "section")[:4]

    context = {
        "students_count": total_students,
        "teachers_count": total_teachers,
        "classes_count": total_classes,
        "exams_count": total_exams,
        "overall_attendance_rate": overall_attendance_rate,
        "jalali_date_str": jalali_date_str,
        "recent_students": recent_students,
        "recent_classes": recent_classes,
    }
    return render(request, "dashboard/dashboard.html", context)


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Students SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "dashboard/students/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        return Student.objects.select_related("status").prefetch_related(
            "studentclass__classs"
        ).order_by("-id")


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "dashboard/students/student_detail.html"
    context_object_name = "student"


@is_admin
def disable_student(request, id):
    target = get_object_or_404(Student, id=id)
    target.detached_date = str(jdatetime.date.today())
    target.status_id = 2
    target.save()
    messages.success(request, f"پرونده دانش‌آموز «{target.name}» با موفقیت غیرفعال گردید.")
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
                    student=student,academice_year=academice_year_obj).first()
                if student_class:
                    student_class.classs = class_obj
                    student_class.save()
                else:
                    StudentClass.objects.create(
                        student=student, classs=class_obj, academice_year=academice_year_obj)
        else:
            return render(request, "dashboard/students/student_edite.html", {"student": student, "classes": classes, "errors": form.errors})
        return redirect(reverse("dashboard:student-detail", kwargs={"pk": student.id}))
    else:
        return render(request, "dashboard/students/student_edite.html", {"student": student, "classes": classes})


@is_admin
def student_create(request):
    classes = Classes.objects.all()
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            print(form.data)
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
            mother_language = Language.objects.get(
                id=int(form.cleaned_data["mother_language"]))
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
                mother_language=mother_language,
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
            academice_year_obj = AcademiceYear.objects.filter(
                year=academice_year).first()
            class_obj =Classes.objects.filter(
                grade=grade, section=section,academice_year=academice_year_obj)
            StudentClass.objects.create(
                student=new_student, classs=class_obj, academice_year=academice_year_obj)
            return redirect(reverse("dashboard:student-list"))
        else:
            return render(request, "dashboard/students/student_edite.html", {"classes": classes, "errors": form.errors})
    else:
        return render(request, "dashboard/students/student_edite.html", {"classes": classes})

# -----------------------------------------------------------------------------
#####
#####
######### -------------- TEACHERS ANS WORKERS SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = "dashboard/workers/workers_list.html"
    context_object_name = "workers"

    def get_queryset(self):
        return Teacher.objects.select_related("job", "degree", "status").order_by("-id")


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = "dashboard/workers/worker_detail.html"
    context_object_name = "worker"

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
            guidence_at = form.cleaned_data.get("guidence_at")
            if guidence_at and "-" in str(guidence_at):
                grade, section = guidence_at.split("-")
                class_obj = Classes.objects.filter(
                    grade=int(grade), section=section).first()
                if class_obj:
                    class_obj.guidence = new_teacher
                    class_obj.save()

            messages.success(
                request, f"استاد/کارمند جدید ({new_teacher.name} {new_teacher.last_name}) با موفقیت در سامانه ثبت شد.")
            return redirect(reverse("dashboard:worker-list"))
        else:
            return render(request, "dashboard/workers/worker_edite.html", {"classes": classes, "errors": form.errors})
    else:
        return render(request, "dashboard/workers/worker_edite.html", {"classes": classes})



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
                teacher.status.id = int(form.cleaned_data["status"])
            teacher.save()
            guidence_at = form.cleaned_data.get("guidence_at")
            if guidence_at and "-" in str(guidence_at):
                grade, section = guidence_at.split("-")
                class_obj = Classes.objects.filter(
                    grade=int(grade), section=section).first()
                if class_obj:
                    # Remove any previous class where this teacher was guidence
                    Classes.objects.filter(guidence=teacher).exclude(
                        id=class_obj.id).update(guidence=None)
                    class_obj.guidence = teacher
                    class_obj.save()
            elif guidence_at in ["None", "", None]:
                Classes.objects.filter(guidence=teacher).update(guidence=None)
            messages.success(
                request, f"اطلاعات پرونده {teacher.name} {teacher.last_name} با موفقیت به‌روزرسانی شد.")
            return redirect(reverse("dashboard:worker-detail", kwargs={"pk": teacher.id}))
        else:
            return render(request, "dashboard/workers/worker_edite.html", {"teacher": teacher, "classes": classes, "errors": form.errors})

    else:
        return render(request, "dashboard/workers/worker_edite.html", {"teacher": teacher, "classes": classes})


@is_admin
def disable_teacher(request, id):
    target = get_object_or_404(Teacher, id=id)
    target.detached_date = str(jdatetime.date.today())
    target.status_id = 2
    target.save()
    messages.success(request, f"پرونده استاد «{target.name} {target.last_name}» با موفقیت غیرفعال گردید.")
    return redirect(reverse("dashboard:worker-list"))


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Classes SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

class ClassesListView(LoginRequiredMixin, ListView):
    model = Classes
    template_name = "dashboard/classes/class_list.html"
    context_object_name = "classes"

    def get_queryset(self):
        return Classes.objects.select_related(
            "guidence", "academice_year", "status"
        ).prefetch_related("studentclass").order_by("grade", "section")

    def get_context_data(self, **kwargs) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context["teachers_count"] = Teacher.objects.count()
        context["students_count"] = Student.objects.count()
        return context


class ClassDetailView(LoginRequiredMixin, DetailView):
    model = Classes
    template_name = "dashboard/classes/class_detail.html"
    context_object_name = "class"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_obj = self.get_object()
        students_count = class_obj.studentclass.count()
        capacity = class_obj.capacity
        completion_percentage = (
            students_count / capacity) * 100 if capacity > 0 else 0
        context['completion_percentage'] = round(completion_percentage, 1)
        context['students_count'] = students_count
        context['remain'] = capacity - students_count
        return context


@is_admin
def class_create(request):
    teachers = Teacher.objects.filter(classes__isnull=True).order_by("name")
    academic_years = AcademiceYear.objects.all().order_by("-year")
    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            academice_year = int(form.cleaned_data["academice_year"])
            academice_year_obj = AcademiceYear.objects.get(year=academice_year)
            grade, alpha_grade = form.cleaned_data["grade"].split("-")
            section = form.cleaned_data["section"]
            capacity = form.cleaned_data["capacity"]
            guidence_id = form.cleaned_data["guidence"]
            start_time_hour = form.cleaned_data["start_time_hour"]
            start_time_minute = form.cleaned_data["start_time_minute"]
            end_time_hour = form.cleaned_data["end_time_hour"]
            end_time_minute = form.cleaned_data["end_time_minute"]
            teacher = teachers.get(id=guidence_id)
            new_cls = Classes.objects.create(
                academice_year=academice_year_obj,
                grade=int(grade),
                alpha_grade=alpha_grade,
                section=section,
                capacity=capacity,
                guidence=teacher,
                start_time=f"{start_time_hour:02d}:{start_time_minute:02d}",
                end_time=f"{end_time_hour:02d}:{end_time_minute:02d}"
            )
            messages.success(
                request, f"صنف جدید ({new_cls.alpha_grade} شعبه {new_cls.section}) با موفقیت ایجاد شد.")
            return redirect(reverse("dashboard:class-list"))
        else:
            return redirect(reverse("dashboard:class-register"))
    return render(request, "dashboard/classes/class_edite.html", {"teachers": teachers, "academic_years": academic_years})


@is_admin
def class_edite(request, id):
    class_obj = get_object_or_404(Classes, id=id)
    teachers = Teacher.objects.filter(Q(classes=class_obj) | Q(
        classes__isnull=True)).distinct().order_by("name")
    academic_years = AcademiceYear.objects.all().order_by("-year")
    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            academice_year = int(form.cleaned_data["academice_year"])
            academice_year_obj = AcademiceYear.objects.get(year=academice_year)
            grade, alpha_grade = form.cleaned_data["grade"].split("-")
            section = form.cleaned_data["section"]
            capacity = form.cleaned_data["capacity"]
            guidence_id = form.cleaned_data["guidence"]
            start_time_hour = form.cleaned_data["start_time_hour"]
            start_time_minute = form.cleaned_data["start_time_minute"]
            end_time_hour = form.cleaned_data["end_time_hour"]
            end_time_minute = form.cleaned_data["end_time_minute"]
            if class_obj.academice_year != academice_year_obj:
                class_obj.academice_year = academice_year_obj
            if class_obj.grade != int(grade):
                class_obj.grade = int(grade)
            if class_obj.alpha_grade != alpha_grade:
                class_obj.alpha_grade = alpha_grade
            if class_obj.section != section:
                class_obj.section = section
            if class_obj.capacity != capacity:
                class_obj.capacity = capacity
            if class_obj.guidence_id != guidence_id:
                class_obj.guidence_id = guidence_id
            class_obj.start_time = f"{start_time_hour:02d}:{start_time_minute:02d}"
            class_obj.end_time = f"{end_time_hour:02d}:{end_time_minute:02d}"
            class_obj.save()
            messages.success(
                request, f"مشخصات صنف {class_obj.alpha_grade} شعبه {class_obj.section} با موفقیت به‌روزرسانی شد.")
            return redirect(reverse("dashboard:class-list"))
            
    return render(request, "dashboard/classes/class_edite.html", {"teachers": teachers, "class": class_obj, "academic_years": academic_years})


@is_admin
def class_disable(request, id):
    class_obj = get_object_or_404(Classes, id=id)
    class_obj.status_id = 2
    class_obj.save()
    messages.success(request, f"صنف «{class_obj.grade} - {class_obj.section}» با موفقیت غیرفعال گردید.")
    return redirect(reverse("dashboard:class-list"))
# -----------------------------------------------------------------------------
#####
#####
######### -------------- Attendence SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------


class AttendenceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "dashboard/attendence/attendence.html"
    context_object_name = "attendences"
    paginate_by = 50

    def get_queryset(self):
        qs = Attendance.objects.select_related(
            "student", "classs", "month", "academice_year"
        ).order_by("classs__grade", "classs__section", "student__name")

        class_id = self.request.GET.get("class_id")
        month_id = self.request.GET.get("month_id")
        academic_year_id = self.request.GET.get("academic_year_id")
        search = self.request.GET.get("search")

        if class_id and str(class_id).isdigit():
            qs = qs.filter(classs_id=int(class_id))
        if month_id and str(month_id).isdigit():
            qs = qs.filter(month_id=int(month_id))
        if academic_year_id and str(academic_year_id).isdigit():
            qs = qs.filter(academice_year_id=int(academic_year_id))
        if search:
            search = search.strip()
            qs = qs.filter(
                Q(student__name__icontains=search)
                | Q(student__fname__icontains=search)
                | Q(student__card_id__icontains=search)
                | Q(student__school_id__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = list(self.get_queryset())
        total_records = len(records)

        total_present = sum(r.present for r in records)
        total_absent = sum(r.absent for r in records)
        total_sick = sum(r.sick for r in records)
        total_excused = sum(r.excused for r in records)
        total_alldays = sum(r.alldays for r in records)

        if total_alldays > 0:
            avg_rate = round((total_present / total_alldays) * 100, 1)
        else:
            avg_rate = 0.0

        sample_alldays = records[0].alldays if records else 24

        context["total_records"] = total_records
        context["avg_rate"] = avg_rate
        context["total_absent"] = total_absent
        context["total_sick_excused"] = total_sick + total_excused
        context["sample_alldays"] = sample_alldays

        context["classes"] = Classes.objects.all().order_by("grade", "section")
        context["months"] = Month.objects.all().order_by("id")
        context["academic_years"] = AcademiceYear.objects.all().order_by("-year")

        context["selected_class_id"] = self.request.GET.get("class_id", "")
        context["selected_month_id"] = self.request.GET.get("month_id", "")
        context["selected_year_id"] = self.request.GET.get(
            "academic_year_id", "")
        context["search_query"] = self.request.GET.get("search", "")
        return context


@is_admin
def attendance_create_or_edit(request, class_id=None, month_id=None, academic_year_id=None):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")
    months = Month.objects.all().order_by("id")

    # Determine Academic Year
    selected_year_id = academic_year_id or request.GET.get(
        "academic_year") or request.POST.get("academic_year")
    if selected_year_id and str(selected_year_id).isdigit():
        academic_year_obj = AcademiceYear.objects.filter(
            id=int(selected_year_id)).first()
    else:
        academic_year_obj = academic_years.first()

    # Determine Class
    selected_class_id = class_id or request.GET.get(
        "class") or request.POST.get("class")
    if selected_class_id and str(selected_class_id).isdigit():
        class_obj = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        class_obj = classes.first()

    # Determine Month
    selected_month_id = month_id or request.GET.get(
        "month") or request.POST.get("month")
    if selected_month_id and str(selected_month_id).isdigit():
        month_obj = Month.objects.filter(id=int(selected_month_id)).first()
    else:
        month_obj = months.first()

    # Default all days
    default_all_days = 24
    if request.method == "POST":
        try:
            default_all_days = int(request.POST.get("all_days", 24))
        except (ValueError, TypeError):
            default_all_days = 24

    # Enrolled students for this class and academic year
    student_enrollments = StudentClass.objects.filter(
        classs=class_obj, academice_year=academic_year_obj
    ).select_related("student").order_by("student__name")

    if not student_enrollments.exists() and class_obj:
        student_enrollments = StudentClass.objects.filter(
            classs=class_obj
        ).select_related("student").order_by("student__name")

    # Existing records
    existing_records = {}
    if class_obj and month_obj and academic_year_obj:
        att_qs = Attendance.objects.filter(
            classs=class_obj, month=month_obj, academice_year=academic_year_obj
        )
        for att in att_qs:
            existing_records[att.student_id] = att
            if request.method != "POST":
                default_all_days = att.alldays

    if request.method == "POST":
        saved_count = 0
        all_days = int(request.POST.get("all_days", default_all_days or 24))

        for sc in student_enrollments:
            student = sc.student
            st_id = student.id

            p_val = request.POST.get(f"present_{st_id}")
            a_val = request.POST.get(f"absent_{st_id}")
            s_val = request.POST.get(f"sick_{st_id}")
            e_val = request.POST.get(f"excused_{st_id}")

            if p_val is None:
                continue

            try:
                present = max(0, int(p_val))
            except (ValueError, TypeError):
                present = all_days

            try:
                absent = max(0, int(a_val or 0))
            except (ValueError, TypeError):
                absent = 0

            try:
                sick = max(0, int(s_val or 0))
            except (ValueError, TypeError):
                sick = 0

            try:
                excused = max(0, int(e_val or 0))
            except (ValueError, TypeError):
                excused = 0

            Attendance.objects.update_or_create(
                student=student,
                classs=class_obj,
                month=month_obj,
                academice_year=academic_year_obj,
                defaults={
                    "present": present,
                    "absent": absent,
                    "sick": sick,
                    "excused": excused,
                    "alldays": all_days,
                },
            )
            saved_count += 1

        messages.success(
            request,
            f"کارنامه حاضری صنف {class_obj.grade}-{class_obj.section} برای ماه {month_obj.name} با موفقیت ({saved_count} شاگرد) ذخیره و به‌روزرسانی شد."
        )
        return redirect(
            f"{reverse('dashboard:attendence-list')}?class_id={class_obj.id}&month_id={month_obj.id}&academic_year_id={academic_year_obj.id}"
        )

    # Prepare rows for GET display
    student_rows = []
    total_present_sum = 0
    total_absent_sum = 0
    total_sick_sum = 0
    total_excused_sum = 0

    for sc in student_enrollments:
        student = sc.student
        rec = existing_records.get(student.id)
        if rec:
            p = rec.present
            a = rec.absent
            s = rec.sick
            e = rec.excused
            ad = rec.alldays
            pct = rec.get_present_percentage()
            is_new = False
        else:
            p = default_all_days
            a = 0
            s = 0
            e = 0
            ad = default_all_days
            pct = 100
            is_new = True

        total_present_sum += p
        total_absent_sum += a
        total_sick_sum += s
        total_excused_sum += e

        student_rows.append({
            "student": student,
            "present": p,
            "absent": a,
            "sick": s,
            "excused": e,
            "alldays": ad,
            "percentage": pct,
            "is_new": is_new,
        })

    student_count = len(student_rows)
    class_all_days = default_all_days or 24
    if student_count > 0 and class_all_days > 0:
        class_avg_rate = round(
            (total_present_sum / (student_count * class_all_days)) * 100, 1)
    else:
        class_avg_rate = 100.0 if student_count > 0 else 0.0

    has_existing_records = bool(existing_records)

    context = {
        "academic_years": academic_years,
        "classes": classes,
        "months": months,
        "selected_year": academic_year_obj,
        "selected_class": class_obj,
        "selected_month": month_obj,
        "all_days": class_all_days,
        "student_rows": student_rows,
        "student_count": student_count,
        "has_existing_records": has_existing_records,
        "class_avg_rate": class_avg_rate,
        "total_absent_sum": total_absent_sum,
    }
    return render(request, "dashboard/attendence/attendence_edite.html", context)


@is_admin
def attendence_create(request, academic_year=None, class_section=None):
    return attendance_create_or_edit(request)


@is_admin
def attendence_edite(request, class_id=None, month_id=None, academic_year_id=None):
    return attendance_create_or_edit(request, class_id=class_id, month_id=month_id, academic_year_id=academic_year_id)

# -----------------------------------------------------------------------------
#####
#####
######### -------------- Assesment SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------


class AssesmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = "dashboard/assesment.html"
    context_object_name = "assesments"

# -----------------------------------------------------------------------------
#####
#####
######### -------------- Exam SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------


class ExamListView(LoginRequiredMixin, ListView):
    model = ExamResult
    template_name = "dashboard/exam.html"
    context_object_name = "exams"


@is_admin
def finance_view(request):
    return render(request, "dashboard/finance/finance.html")
