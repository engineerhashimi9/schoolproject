from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count, F
from decimal import Decimal
import jdatetime
import datetime

from .models import (
    Student, Teacher, Classes, Job, StudentClass,
    AcademiceYear, Degree, Attendance, Assessment,
    ExamResult, Exam, Month, Language, Subject, Fee,
    ExamMark, ExamAttendance, Shaqqa, Expense, TimeTable, TeacherSubject
)
from .forms import StudentForm, TeacherForm, ClassForm, SubjectForm
from .services.teacher_service import (
    get_current_teacher_profile,
    get_teacher_assigned_classes,
    get_teacher_assigned_subjects,
    get_teacher_today_schedule,
    get_teacher_kpis,
    get_teacher_shaqqa_matrix,
    save_teacher_shaqqa_matrix,
)
from .services.subject_service import (
    get_afghan_curriculum_standards,
    apply_afghan_curriculum_to_class,
    get_subject_statistics,
    get_subject_detail_metrics,
    validate_subject_deletion,
    get_class_educational_stage,
)
from .services.exam_service import (
    calculate_class_results,
    calculate_student_result,
    get_class_subjects,
    calculate_grade,
    format_rank_afghan,
)
from .services.finance_service import (
    number_to_dari_words,
    calculate_finance_kpis,
    calculate_financial_report,
)
from .services.timetable_service import (
    get_class_timetable_matrix,
    get_teacher_timetable_matrix,
    validate_timetable_slot,
    get_master_timetable_matrix,
    DAYS,
    PERIODS,
    RECESS_INFO,
)


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Security And Helpers SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        if hasattr(request.user, "teacher_profile") and request.user.teacher_profile:
            return redirect(reverse("teachers:dashboard"))
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

    # Financial & Timetable KPIs
    fee_collected = Fee.objects.aggregate(total=Sum("paied"))["total"] or 0
    expenses_total = Expense.objects.aggregate(
        total=Sum("amount"))["total"] or 0
    net_balance = fee_collected - expenses_total
    timetable_count = TimeTable.objects.count()
    shaqqa_count = ExamMark.objects.count()

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
        "fee_collected": fee_collected,
        "expenses_total": expenses_total,
        "net_balance": net_balance,
        "timetable_count": timetable_count,
        "shaqqa_count": shaqqa_count,
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
    messages.success(
        request, f"پرونده دانش‌آموز «{target.name}» با موفقیت غیرفعال گردید.")
    return redirect(reverse("dashboard:student-list"))


@is_admin
def student_edite(request, id):
    student = get_object_or_404(Student, id=id)
    classes = Classes.objects.all().order_by("grade", "section")
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student.school_id = form.cleaned_data["school_id"]
            student.card_id = form.cleaned_data["card_id"]
            student.name = form.cleaned_data["name"]
            student.fname = form.cleaned_data["fname"]
            student.gfname = form.cleaned_data["gfname"]
            student.birth_date = form.cleaned_data["birth_date"]
            student.nationality = form.cleaned_data["nationality"]

            fjob_str = form.cleaned_data.get("father_job")
            if fjob_str:
                fjob, _ = Job.objects.get_or_create(name=fjob_str.strip())
                student.father_job = fjob

            student.phone = form.cleaned_data["phone"]
            student.mother_language_id = int(
                form.cleaned_data["mother_language"])
            student.status_id = int(form.cleaned_data["status"])
            student.registered_date = form.cleaned_data["registered_date"]

            student.now_province_id = int(form.cleaned_data["now_province"])
            student.now_district_id = int(form.cleaned_data["now_district"])
            student.now_zone = int(form.cleaned_data["now_zone"])
            student.now_village = form.cleaned_data["now_village"]

            student.original_province_id = int(
                form.cleaned_data["original_province"])
            student.original_district_id = int(
                form.cleaned_data["original_district"])
            student.original_zone = int(form.cleaned_data["original_zone"])
            student.original_village = form.cleaned_data["original_village"]
            student.save()

            if "class_section" in form.cleaned_data:
                grade, section = form.cleaned_data["class_section"].split("-")
                academice_year = int(form.cleaned_data["academice_year"])
                academice_year_obj = AcademiceYear.objects.filter(
                    year=academice_year).first() or AcademiceYear.objects.first()
                class_obj = Classes.objects.filter(
                    grade=int(grade), section=section).first()
                if class_obj and academice_year_obj:
                    student_class = StudentClass.objects.filter(
                        student=student, academice_year=academice_year_obj).first()
                    if student_class:
                        student_class.classs = class_obj
                        student_class.save()
                    else:
                        StudentClass.objects.create(
                            student=student, classs=class_obj, academice_year=academice_year_obj)
            messages.success(
                request, f"پرونده دانش‌آموز «{student.name}» با موفقیت به‌روزرسانی شد.")
            return redirect(reverse("dashboard:student-detail", kwargs={"pk": student.id}))
        else:
            return render(request, "dashboard/students/student_edite.html", {"student": student, "classes": classes, "errors": form.errors})
    else:
        return render(request, "dashboard/students/student_edite.html", {"student": student, "classes": classes})


@is_admin
def student_create(request):
    classes = Classes.objects.all().order_by("grade", "section")
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
            father_job, _ = Job.objects.get_or_create(
                name=form.cleaned_data["father_job"].strip())
            phone = form.cleaned_data["phone"]
            mother_language = Language.objects.get(
                id=int(form.cleaned_data["mother_language"]))
            status_id = int(form.cleaned_data["status"])
            registered_date = form.cleaned_data["registered_date"]
            grade, section = form.cleaned_data["class_section"].split("-")
            now_province_id = int(form.cleaned_data["now_province"])
            now_district_id = int(form.cleaned_data["now_district"])
            now_zone = int(form.cleaned_data["now_zone"])
            now_village = form.cleaned_data["now_village"]
            original_province_id = int(form.cleaned_data["original_province"])
            original_district_id = int(form.cleaned_data["original_district"])
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
                status_id=status_id,
                registered_date=registered_date,
                now_province_id=now_province_id,
                now_district_id=now_district_id,
                now_zone=now_zone,
                now_village=now_village,
                original_province_id=original_province_id,
                original_district_id=original_district_id,
                original_zone=original_zone,
                original_village=original_village
            )
            academice_year_obj = AcademiceYear.objects.filter(
                year=academice_year).first() or AcademiceYear.objects.first()
            class_obj = Classes.objects.filter(
                grade=int(grade), section=section).first()
            if class_obj and academice_year_obj:
                StudentClass.objects.create(
                    student=new_student, classs=class_obj, academice_year=academice_year_obj)
            messages.success(
                request, f"دانش‌آموز «{new_student.name}» با موفقیت در سامانه پذیرش و ثبت‌نام شد.")
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
            teacher.name = form.cleaned_data["name"]
            teacher.fname = form.cleaned_data["fname"]
            teacher.last_name = form.cleaned_data["last_name"]
            teacher.phone = form.cleaned_data["phone"]
            teacher.major = form.cleaned_data["major"]

            degree_name = form.cleaned_data.get("degree")
            if degree_name:
                degree, _ = Degree.objects.get_or_create(
                    name=degree_name.strip())
                teacher.degree = degree

            job_name = form.cleaned_data.get("job")
            if job_name:
                job, _ = Job.objects.get_or_create(name=job_name.strip())
                teacher.job = job

            teacher.years_of_service = form.cleaned_data["years_of_service"]
            teacher.registered_date = form.cleaned_data["registered_date"]
            teacher.detached_date = form.cleaned_data.get("detached_date")
            teacher.graduation_year = form.cleaned_data["graduation_year"]
            teacher.salary = form.cleaned_data["salary"]
            teacher.tax = form.cleaned_data["tax"]
            if form.cleaned_data.get("status"):
                teacher.status_id = int(form.cleaned_data["status"])
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
    messages.success(
        request, f"پرونده استاد «{target.name} {target.last_name}» با موفقیت غیرفعال گردید.")
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
            academice_year_obj = AcademiceYear.objects.filter(
                year=academice_year).first()
            if not academice_year_obj:
                academice_year_obj = AcademiceYear.objects.get_or_create(year=academice_year)[
                    0]
            grade, alpha_grade = form.cleaned_data["grade"].split("-")
            section = form.cleaned_data["section"]
            capacity = form.cleaned_data["capacity"]
            guidence_id = form.cleaned_data.get("guidence")
            start_time_hour = form.cleaned_data["start_time_hour"]
            start_time_minute = form.cleaned_data["start_time_minute"]
            end_time_hour = form.cleaned_data["end_time_hour"]
            end_time_minute = form.cleaned_data["end_time_minute"]

            guidence_teacher = None
            if guidence_id and str(guidence_id).isdigit():
                guidence_teacher = Teacher.objects.filter(
                    id=int(guidence_id)).first()

            new_cls = Classes.objects.create(
                academice_year=academice_year_obj,
                grade=int(grade),
                alpha_grade=alpha_grade,
                section=section,
                capacity=capacity,
                guidence=guidence_teacher,
                start_time=f"{start_time_hour:02d}:{start_time_minute:02d}",
                end_time=f"{end_time_hour:02d}:{end_time_minute:02d}"
            )
            messages.success(
                request, f"صنف جدید ({new_cls.alpha_grade} شعبه {new_cls.section}) با موفقیت ایجاد شد.")
            return redirect(reverse("dashboard:class-list"))
        else:
            messages.error(
                request, "لطفاً خطاهای فرم ثبت صنف را تصحیح نمایید.")
            return render(request, "dashboard/classes/class_edite.html", {"teachers": teachers, "academic_years": academic_years, "errors": form.errors})
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
            academice_year_obj = AcademiceYear.objects.filter(
                year=academice_year).first()
            if not academice_year_obj:
                academice_year_obj = AcademiceYear.objects.get_or_create(year=academice_year)[
                    0]
            grade, alpha_grade = form.cleaned_data["grade"].split("-")
            section = form.cleaned_data["section"]
            capacity = form.cleaned_data["capacity"]
            guidence_id = form.cleaned_data.get("guidence")
            start_time_hour = form.cleaned_data["start_time_hour"]
            start_time_minute = form.cleaned_data["start_time_minute"]
            end_time_hour = form.cleaned_data["end_time_hour"]
            end_time_minute = form.cleaned_data["end_time_minute"]

            class_obj.academice_year = academice_year_obj
            class_obj.grade = int(grade)
            class_obj.alpha_grade = alpha_grade
            class_obj.section = section
            class_obj.capacity = capacity

            if guidence_id and str(guidence_id).isdigit():
                class_obj.guidence_id = int(guidence_id)
            else:
                class_obj.guidence = None

            class_obj.start_time = f"{start_time_hour:02d}:{start_time_minute:02d}"
            class_obj.end_time = f"{end_time_hour:02d}:{end_time_minute:02d}"
            class_obj.save()
            messages.success(
                request, f"مشخصات صنف {class_obj.alpha_grade} شعبه {class_obj.section} با موفقیت به‌روزرسانی شد.")
            return redirect(reverse("dashboard:class-list"))
        else:
            messages.error(
                request, "لطفاً خطاهای فرم ویرایش صنف را تصحیح نمایید.")
            return render(request, "dashboard/classes/class_edite.html", {"teachers": teachers, "class": class_obj, "academic_years": academic_years, "errors": form.errors})

    return render(request, "dashboard/classes/class_edite.html", {"teachers": teachers, "class": class_obj, "academic_years": academic_years})


@is_admin
def class_disable(request, id):
    class_obj = get_object_or_404(Classes, id=id)
    class_obj.status_id = 2
    class_obj.save()
    messages.success(
        request, f"صنف «{class_obj.grade} - {class_obj.section}» با موفقیت غیرفعال گردید.")
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

# Asisment list view has checked and have not any probelm


class AssesmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = "dashboard/assesment/assesment.html"
    context_object_name = "assesments"
    paginate_by = 20

    def get_queryset(self):
        qs = Assessment.objects.select_related(
            "student", "teacher", "subject", "classs", "month", "academice_year"
        ).order_by("-id")

        class_id = self.request.GET.get("class_id")
        subject_id = self.request.GET.get("subject_id")
        teacher_id = self.request.GET.get("teacher_id")
        month_id = self.request.GET.get("month_id")
        academic_year_id = self.request.GET.get("academic_year_id")
        search = self.request.GET.get("search")

        if class_id and str(class_id).isdigit():
            qs = qs.filter(classs_id=int(class_id))
        if subject_id and str(subject_id).isdigit():
            qs = qs.filter(subject_id=int(subject_id))
        if teacher_id and str(teacher_id).isdigit():
            qs = qs.filter(teacher_id=int(teacher_id))
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

        if total_records > 0:
            percentages = [r.getPercentage() for r in records]
            avg_score = round(sum(percentages) / total_records, 1)
            highest_rec = max(records, key=lambda r: r.getPercentage())
            needs_help = sum(1 for p in percentages if p < 60)
        else:
            avg_score = 0.0
            highest_rec = None
            needs_help = 0

        context["total_records"] = total_records
        context["avg_score"] = avg_score
        context["highest_rec"] = highest_rec
        context["needs_help_count"] = needs_help

        context["classes"] = Classes.objects.all().order_by("grade", "section")
        context["subjects"] = Subject.objects.all().order_by("name")
        context["teachers"] = Teacher.objects.filter(
            status_id=1).order_by("name", "last_name")
        context["months"] = Month.objects.all().order_by("id")
        context["academic_years"] = AcademiceYear.objects.all().order_by("-year")

        context["selected_class_id"] = self.request.GET.get("class_id", "")
        context["selected_subject_id"] = self.request.GET.get("subject_id", "")
        context["selected_teacher_id"] = self.request.GET.get("teacher_id", "")
        context["selected_month_id"] = self.request.GET.get("month_id", "")
        context["selected_year_id"] = self.request.GET.get(
            "academic_year_id", "")
        context["search_query"] = self.request.GET.get("search", "")
        return context


@is_admin
def assesment_create(request):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")
    subjects = Subject.objects.all().order_by("name")
    teachers = Teacher.objects.filter(
        status_id=1).order_by("name", "last_name")
    months = Month.objects.all().order_by("id")

    # Mode: "batch" (class roster grading) or "single"
    mode = request.GET.get("mode") or request.POST.get("mode") or "batch"

    selected_year_id = request.GET.get(
        "academic_year") or request.POST.get("academic_year")
    if selected_year_id and str(selected_year_id).isdigit():
        year_obj = AcademiceYear.objects.filter(
            id=int(selected_year_id)).first()
    else:
        year_obj = academic_years.first()

    selected_class_id = request.GET.get("class") or request.POST.get("class")
    if selected_class_id and str(selected_class_id).isdigit():
        class_obj = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        class_obj = classes.first()

    selected_subject_id = request.GET.get(
        "subject") or request.POST.get("subject")
    if selected_subject_id and str(selected_subject_id).isdigit():
        subject_obj = Subject.objects.filter(
            id=int(selected_subject_id)).first()
    else:
        subject_obj = subjects.first()

    selected_month_id = request.GET.get("month") or request.POST.get("month")
    if selected_month_id and str(selected_month_id).isdigit():
        month_obj = Month.objects.filter(id=int(selected_month_id)).first()
    else:
        month_obj = months.first()

    selected_teacher_id = request.GET.get(
        "teacher") or request.POST.get("teacher")
    if selected_teacher_id and str(selected_teacher_id).isdigit():
        teacher_obj = Teacher.objects.filter(
            id=int(selected_teacher_id)).first()
    elif class_obj and class_obj.guidence:
        teacher_obj = class_obj.guidence
    else:
        teacher_obj = teachers.first()

    default_max_score = 100
    max_score_input = request.GET.get(
        "max_score") or request.POST.get("max_score")
    if max_score_input and str(max_score_input).isdigit():
        default_max_score = int(max_score_input)

    if request.method == "POST":
        action_type = request.POST.get("action_type", "batch")

        if action_type == "single":
            student_id = request.POST.get("student")
            score_val = request.POST.get("score")
            max_val = request.POST.get("single_max_score", 100)

            if student_id and score_val is not None:
                student = get_object_or_404(Student, id=int(student_id))
                try:
                    score = int(score_val)
                    max_score = max(1, int(max_val or 100))
                except (ValueError, TypeError):
                    score = 0
                    max_score = 100

                Assessment.objects.update_or_create(
                    student=student,
                    subject=subject_obj,
                    month=month_obj,
                    academice_year=year_obj,
                    defaults={
                        "classs": class_obj,
                        "teacher": teacher_obj,
                        "score": score,
                        "max_score": max_score,
                    }
                )
                messages.success(
                    request, f"نمره ارزیابی شاگرد «{student.name}» با موفقیت ثبت شد.")
                return redirect(f"{reverse('dashboard:assesment-list')}?class_id={class_obj.id}&subject_id={subject_obj.id}&month_id={month_obj.id}&academic_year_id={year_obj.id}")
        else:
            student_enrollments = StudentClass.objects.filter(
                classs=class_obj,
                academice_year=year_obj
            ).select_related("student")

            saved_count = 0
            for sc in student_enrollments:
                student = sc.student
                score_key = f"score_{student.id}"
                max_key = f"max_score_{student.id}"

                if score_key in request.POST:
                    raw_score = request.POST.get(score_key)
                    raw_max = request.POST.get(max_key, default_max_score)
                    if raw_score is not None and str(raw_score).strip() != "":
                        try:
                            score = int(raw_score)
                            max_sc = max(1, int(raw_max or default_max_score))
                        except (ValueError, TypeError):
                            score = 0
                            max_sc = default_max_score

                        Assessment.objects.update_or_create(
                            student=student,
                            subject=subject_obj,
                            month=month_obj,
                            academice_year=year_obj,
                            defaults={
                                "classs": class_obj,
                                "teacher": teacher_obj,
                                "score": score,
                                "max_score": max_sc,
                            }
                        )
                        saved_count += 1

            messages.success(
                request,
                f"نمرات ارزیابی مضمون «{subject_obj.name}» برای صنف {class_obj.grade}-{class_obj.section} در ماه {month_obj.name} با موفقیت ({saved_count} شاگرد) ذخیره و به‌روزرسانی شد."
            )
            return redirect(f"{reverse('dashboard:assesment-list')}?class_id={class_obj.id}&subject_id={subject_obj.id}&month_id={month_obj.id}&academic_year_id={year_obj.id}")

    # Prepare class roster for GET
    student_enrollments = StudentClass.objects.filter(
        classs=class_obj,
        academice_year=year_obj
    ).select_related("student") if class_obj and year_obj else []

    existing_assessments = {}
    if class_obj and subject_obj and month_obj and year_obj:
        for a in Assessment.objects.filter(
            classs=class_obj,
            subject=subject_obj,
            month=month_obj,
            academice_year=year_obj
        ):
            existing_assessments[a.student_id] = a

    student_rows = []
    for sc in student_enrollments:
        student = sc.student
        rec = existing_assessments.get(student.id)
        if rec:
            sc_val = rec.score
            mx_val = rec.max_score
            is_new = False
            pct = rec.getPercentage()
            rank_label = rec.get_student_rank()
        else:
            sc_val = ""
            mx_val = default_max_score
            is_new = True
            pct = 0
            rank_label = "ثبت‌نشده"

        student_rows.append({
            "student": student,
            "score": sc_val,
            "max_score": mx_val,
            "percentage": pct,
            "rank_label": rank_label,
            "is_new": is_new,
        })

    all_students = Student.objects.filter(status_id=1).order_by("name")

    context = {
        "is_edit_mode": False,
        "academic_years": academic_years,
        "classes": classes,
        "subjects": subjects,
        "teachers": teachers,
        "months": months,
        "all_students": all_students,
        "selected_year": year_obj,
        "selected_class": class_obj,
        "selected_subject": subject_obj,
        "selected_teacher": teacher_obj,
        "selected_month": month_obj,
        "default_max_score": default_max_score,
        "student_rows": student_rows,
        "student_count": len(student_rows),
        "existing_count": len(existing_assessments),
        "mode": mode,
    }
    return render(request, "dashboard/assesment/assesment_edite.html", context)


@is_admin
def assesment_edite(request, id):
    assessment = get_object_or_404(
        Assessment.objects.select_related(
            "student", "classs", "subject", "teacher", "month", "academice_year"
        ),
        id=id
    )

    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")
    subjects = Subject.objects.all().order_by("name")
    teachers = Teacher.objects.filter(
        status_id=1).order_by("name", "last_name")
    months = Month.objects.all().order_by("id")
    students = Student.objects.filter(status_id=1).order_by("name")

    if request.method == "POST":
        student_id = request.POST.get("student")
        class_id = request.POST.get("class")
        subject_id = request.POST.get("subject")
        teacher_id = request.POST.get("teacher")
        month_id = request.POST.get("month")
        year_id = request.POST.get("academic_year")
        raw_score = request.POST.get("score")
        raw_max = request.POST.get("max_score")

        if student_id and class_id and subject_id and teacher_id and month_id and year_id:
            assessment.student_id = int(student_id)
            assessment.classs_id = int(class_id)
            assessment.subject_id = int(subject_id)
            assessment.teacher_id = int(teacher_id)
            assessment.month_id = int(month_id)
            assessment.academice_year_id = int(year_id)
            try:
                assessment.score = int(raw_score or 0)
                assessment.max_score = max(1, int(raw_max or 100))
            except (ValueError, TypeError):
                pass
            assessment.save()
            messages.success(
                request, f"نمره ارزیابی شاگرد «{assessment.student.name}» با موفقیت ویرایش و ذخیره شد.")
            return redirect(reverse("dashboard:assesment-list"))

    context = {
        "is_edit_mode": True,
        "assessment": assessment,
        "academic_years": academic_years,
        "classes": classes,
        "subjects": subjects,
        "teachers": teachers,
        "months": months,
        "all_students": students,
        "selected_year": assessment.academice_year,
        "selected_class": assessment.classs,
        "selected_subject": assessment.subject,
        "selected_teacher": assessment.teacher,
        "selected_month": assessment.month,
        "selected_student": assessment.student,
    }
    return render(request, "dashboard/assesment/assesment_edite.html", context)


@is_admin
def assesment_delete(request, id):
    assessment = get_object_or_404(Assessment, id=id)
    student_name = assessment.student.name if assessment.student else "شاگرد"
    subject_name = assessment.subject.name if assessment.subject else "مضمون"
    assessment.delete()
    messages.success(
        request, f"نمره ارزیابی «{student_name}» در مضمون «{subject_name}» با موفقیت حذف گردید.")
    return redirect(reverse("dashboard:assesment-list"))

# -----------------------------------------------------------------------------
#####
#####
######### -------------- Exam SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------


@is_admin
def exam_dashboard_view(request):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")
    selected_year_id = request.GET.get("year_id")
    selected_year = (
        AcademiceYear.objects.filter(id=int(selected_year_id)).first()
        if selected_year_id and str(selected_year_id).isdigit()
        else (AcademiceYear.objects.filter(year=1403).first() or academic_years.first())
    )

    selected_class_id = request.GET.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    results_data = None
    if selected_class and selected_year:
        results_data = calculate_class_results(selected_class, selected_year)

    context = {
        "academic_years": academic_years,
        "classes": classes,
        "selected_year": selected_year,
        "selected_class": selected_class,
        "results_data": results_data,
        "total_classes": classes.count(),
        "total_subjects": Subject.objects.count(),
        "total_exam_marks": ExamMark.objects.count(),
    }
    return render(request, "dashboard/exam/exam_dashboard.html", context)


class ExamListView(LoginRequiredMixin, ListView):
    """Backwards compatibility view for existing exam-list references"""
    model = ExamMark
    template_name = "dashboard/exam/exam_dashboard.html"
    context_object_name = "exams"

    def get(self, request, *args, **kwargs):
        return exam_dashboard_view(request)


@is_admin
def shaqqa_entry_view(request):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")

    selected_year_id = request.GET.get(
        "year_id") or request.POST.get("year_id")
    selected_year = (
        AcademiceYear.objects.filter(id=int(selected_year_id)).first()
        if selected_year_id and str(selected_year_id).isdigit()
        else (AcademiceYear.objects.filter(year=1403).first() or academic_years.first())
    )

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    available_subjects = get_class_subjects(
        selected_class) if selected_class else list(Subject.objects.all())

    selected_subject_id = request.GET.get(
        "subject_id") or request.POST.get("subject_id")
    if selected_subject_id and str(selected_subject_id).isdigit():
        selected_subject = Subject.objects.filter(
            id=int(selected_subject_id)).first()
    else:
        selected_subject = available_subjects[0] if available_subjects else None

    # Enrolled students
    student_enrollments = (
        StudentClass.objects.filter(
            classs=selected_class, academice_year=selected_year)
        .select_related("student")
        .order_by("student__school_id", "student__name")
        if selected_class and selected_year
        else []
    )

    students = [e.student for e in student_enrollments]

    if request.method == "POST":
        saved_count = 0
        for std in students:
            midterm_key = f"midterm_{std.id}"
            final_key = f"final_{std.id}"
            cond_key = f"cond_{std.id}"
            mahroom_key = f"mahroom_{std.id}"
            mazrati_key = f"mazrati_{std.id}"
            notes_key = f"notes_{std.id}"

            if midterm_key in request.POST or final_key in request.POST or mahroom_key in request.POST:
                raw_midterm = request.POST.get(midterm_key, "").strip()
                raw_final = request.POST.get(final_key, "").strip()
                raw_cond = request.POST.get(cond_key, "").strip()
                is_mahroom = bool(request.POST.get(mahroom_key))
                is_mazrati = bool(request.POST.get(mazrati_key))
                notes = request.POST.get(notes_key, "").strip()

                try:
                    midterm_val = min(40.0, max(0.0, float(
                        raw_midterm))) if raw_midterm != "" else 0.0
                except ValueError:
                    midterm_val = 0.0

                try:
                    final_val = min(60.0, max(0.0, float(raw_final))
                                    ) if raw_final != "" else 0.0
                except ValueError:
                    final_val = 0.0

                cond_val = None
                if raw_cond != "":
                    try:
                        cond_val = min(100.0, max(0.0, float(raw_cond)))
                    except ValueError:
                        cond_val = None

                ExamMark.objects.update_or_create(
                    student=std,
                    classs=selected_class,
                    subject=selected_subject,
                    academice_year=selected_year,
                    defaults={
                        "midterm_marks": Decimal(str(midterm_val)),
                        "final_marks": Decimal(str(final_val)),
                        "conditional_marks": Decimal(str(cond_val)) if cond_val is not None else None,
                        "is_mahroom": is_mahroom,
                        "is_mazrati": is_mazrati,
                        "notes": notes,
                    },
                )
                saved_count += 1

        messages.success(
            request,
            f"شقه نمرات مضمون «{selected_subject.name}» برای صنف {selected_class.grade}-{selected_class.section} با موفقیت برای {saved_count} شاگرد ثبت گردید.",
        )
        return redirect(
            f"{reverse('dashboard:exam-shaqqa')}?class_id={selected_class.id}&subject_id={selected_subject.id}&year_id={selected_year.id}"
        )

    # GET request: fetch existing marks
    existing_marks = {}
    if selected_class and selected_subject and selected_year:
        marks_qs = ExamMark.objects.filter(
            classs=selected_class, subject=selected_subject, academice_year=selected_year
        )
        for m in marks_qs:
            existing_marks[m.student_id] = m

    student_rows = []
    for std in students:
        rec = existing_marks.get(std.id)
        student_rows.append({
            "student": std,
            "midterm": float(rec.midterm_marks) if rec and rec.midterm_marks is not None else "",
            "final": float(rec.final_marks) if rec and rec.final_marks is not None else "",
            "conditional": float(rec.conditional_marks) if rec and rec.conditional_marks is not None else "",
            "total": rec.total_marks if rec else 0.0,
            "is_mahroom": rec.is_mahroom if rec else False,
            "is_mazrati": rec.is_mazrati if rec else False,
            "is_passed": rec.is_passed if rec else False,
            "status_label": rec.status_label if rec else "ثبت‌نشده",
            "notes": rec.notes or "" if rec else "",
        })

    context = {
        "academic_years": academic_years,
        "classes": classes,
        "subjects": available_subjects,
        "selected_year": selected_year,
        "selected_class": selected_class,
        "selected_subject": selected_subject,
        "student_rows": student_rows,
        "total_enrolled": len(students),
    }
    return render(request, "dashboard/exam/shaqqa_entry.html", context)


@is_admin
def jadwal_nataij_view(request):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")

    selected_year_id = request.GET.get("year_id")
    selected_year = (
        AcademiceYear.objects.filter(id=int(selected_year_id)).first()
        if selected_year_id and str(selected_year_id).isdigit()
        else (AcademiceYear.objects.filter(year=1403).first() or academic_years.first())
    )

    selected_class_id = request.GET.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    results_data = None
    if selected_class and selected_year:
        results_data = calculate_class_results(selected_class, selected_year)

    context = {
        "academic_years": academic_years,
        "classes": classes,
        "selected_year": selected_year,
        "selected_class": selected_class,
        "results_data": results_data,
        "today_jalali": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/exam/jadwal_nataij.html", context)


@is_admin
def etlanama_view(request, student_id=None):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")

    selected_year_id = request.GET.get("year_id")
    selected_year = (
        AcademiceYear.objects.filter(id=int(selected_year_id)).first()
        if selected_year_id and str(selected_year_id).isdigit()
        else (AcademiceYear.objects.filter(year=1403).first() or academic_years.first())
    )

    selected_class_id = request.GET.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    is_batch = request.GET.get("batch") == "1"

    target_student_id = student_id or request.GET.get("student_id")
    selected_student = None
    if target_student_id and str(target_student_id).isdigit():
        selected_student = Student.objects.filter(
            id=int(target_student_id)).first()

    class_results = None
    report_cards = []
    if selected_class and selected_year:
        class_results = calculate_class_results(selected_class, selected_year)

        if is_batch:
            report_cards = class_results["students_results"]
        elif selected_student:
            for r in class_results["students_results"]:
                if r["student"].id == selected_student.id:
                    report_cards = [r]
                    break
        elif class_results["students_results"]:
            report_cards = [class_results["students_results"][0]]
            selected_student = report_cards[0]["student"]

    all_students_in_class = [
        r["student"] for r in class_results["students_results"]] if class_results else []

    context = {
        "academic_years": academic_years,
        "classes": classes,
        "selected_year": selected_year,
        "selected_class": selected_class,
        "selected_student": selected_student,
        "all_students_in_class": all_students_in_class,
        "class_results": class_results,
        "report_cards": report_cards,
        "is_batch": is_batch,
        "today_jalali": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/exam/etlanama_print.html", context)


@is_admin
def exam_attendance_view(request):
    academic_years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")

    selected_year_id = request.GET.get(
        "year_id") or request.POST.get("year_id")
    selected_year = (
        AcademiceYear.objects.filter(id=int(selected_year_id)).first()
        if selected_year_id and str(selected_year_id).isdigit()
        else (AcademiceYear.objects.filter(year=1403).first() or academic_years.first())
    )

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    enrollments = (
        StudentClass.objects.filter(
            classs=selected_class, academice_year=selected_year)
        .select_related("student")
        .order_by("student__school_id", "student__name")
        if selected_class and selected_year
        else []
    )

    students = [e.student for e in enrollments]

    if request.method == "POST":
        saved_count = 0
        for std in students:
            m_p = int(request.POST.get(f"m_pres_{std.id}", 0) or 0)
            m_a = int(request.POST.get(f"m_abs_{std.id}", 0) or 0)
            m_s = int(request.POST.get(f"m_sick_{std.id}", 0) or 0)
            m_l = int(request.POST.get(f"m_leave_{std.id}", 0) or 0)

            f_p = int(request.POST.get(f"f_pres_{std.id}", 0) or 0)
            f_a = int(request.POST.get(f"f_abs_{std.id}", 0) or 0)
            f_s = int(request.POST.get(f"f_sick_{std.id}", 0) or 0)
            f_l = int(request.POST.get(f"f_leave_{std.id}", 0) or 0)

            ExamAttendance.objects.update_or_create(
                student=std,
                classs=selected_class,
                academice_year=selected_year,
                defaults={
                    "midterm_present": m_p,
                    "midterm_absent": m_a,
                    "midterm_sick": m_s,
                    "midterm_leave": m_l,
                    "final_present": f_p,
                    "final_absent": f_a,
                    "final_sick": f_s,
                    "final_leave": f_l,
                },
            )
            saved_count += 1

        messages.success(
            request,
            f"ضوابط حاضری امتحانات برای صنف {selected_class.grade}-{selected_class.section} با موفقیت ({saved_count} شاگرد) ذخیره شد.",
        )
        return redirect(
            f"{reverse('dashboard:exam-attendance')}?class_id={selected_class.id}&year_id={selected_year.id}"
        )

    existing_att = {}
    if selected_class and selected_year:
        for att in ExamAttendance.objects.filter(classs=selected_class, academice_year=selected_year):
            existing_att[att.student_id] = att

    rows = []
    for std in students:
        att = existing_att.get(std.id)
        rows.append({
            "student": std,
            "midterm_present": att.midterm_present if att else 0,
            "midterm_absent": att.midterm_absent if att else 0,
            "midterm_sick": att.midterm_sick if att else 0,
            "midterm_leave": att.midterm_leave if att else 0,
            "final_present": att.final_present if att else 0,
            "final_absent": att.final_absent if att else 0,
            "final_sick": att.final_sick if att else 0,
            "final_leave": att.final_leave if att else 0,
            "total_present": att.total_present if att else 0,
            "total_absent": att.total_absent if att else 0,
            "total_days": att.total_days if att else 0,
        })

    context = {
        "academic_years": academic_years,
        "classes": classes,
        "selected_year": selected_year,
        "selected_class": selected_class,
        "rows": rows,
        "total_enrolled": len(students),
    }
    return render(request, "dashboard/exam/exam_attendance.html", context)


@is_admin
def exam_subjects_view(request):
    classes = Classes.objects.all().order_by("grade", "section")
    all_subjects = Subject.objects.all().order_by("name")

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else classes.first()
    )

    if request.method == "POST":
        if "action_assign" in request.POST and selected_class:
            selected_subject_ids = request.POST.getlist("subject_ids")
            selected_class.subjects.set(selected_subject_ids)
            messages.success(
                request,
                f"مضامین رسمی برای صنف {selected_class.grade}-{selected_class.section} با موفقیت به‌روزرسانی شدند.",
            )
            return redirect(f"{reverse('dashboard:exam-subjects')}?class_id={selected_class.id}")
        elif "action_new_subject" in request.POST:
            subj_name = request.POST.get("new_subject_name", "").strip()
            if subj_name:
                Subject.objects.get_or_create(name=subj_name)
                messages.success(
                    request, f"مضمون جدید «{subj_name}» با موفقیت در سیستم ثبت گردید.")
            return redirect(reverse("dashboard:exam-subjects"))

    current_assigned_ids = set(selected_class.subjects.values_list(
        "id", flat=True)) if selected_class else set()

    context = {
        "classes": classes,
        "all_subjects": all_subjects,
        "selected_class": selected_class,
        "current_assigned_ids": current_assigned_ids,
    }
    return render(request, "dashboard/exam/subject_assignment.html", context)


# -----------------------------------------------------------------------------
#####
#####
######### -------------- School Finance & Accounting SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

class FinanceListView(ListView):
    model = Fee
    template_name = "dashboard/finance/finance.html"
    context_object_name = "fees"

    def get_queryset(self) -> QuerySet[Any, Any]:
        qs = Fee.objects.select_related(
            "student", "class_section", "month", "academice_year"
        ).order_by("-payment_date", "-id")

        class_id = self.request.GET.get("class_id")
        month_id = self.request.GET.get("month_id")
        year_id = self.request.GET.get("year_id")
        fee_type = self.request.GET.get("fee_type")
        search = self.request.GET.get("search")

        if class_id and str(class_id).isdigit():
            qs = qs.filter(class_section_id=int(class_id))
        if month_id and str(month_id).isdigit():
            qs = qs.filter(month_id=int(month_id))

        if year_id and year_id != "all":
            if str(year_id).isdigit():
                qs = qs.filter(academice_year_id=int(year_id))
        elif year_id is None:
            # Default to active year (1403 or latest) if not explicitly set
            y1403 = AcademiceYear.objects.filter(year=1403).first()
            if y1403:
                qs = qs.filter(academice_year=y1403)

        if fee_type and str(fee_type).isdigit():
            ft = int(fee_type)
            if ft == 1:
                qs = qs.filter(paied__gte=F("amount"))
            elif ft == 2:
                qs = qs.filter(paied__gt=0, paied__lt=F("amount"))
            elif ft == 3:
                qs = qs.filter(paied__lt=F("amount"))

        if search:
            search = search.strip()
            qs = qs.filter(
                Q(student__name__icontains=search)
                | Q(student__fname__icontains=search)
                | Q(student__card_id__icontains=search)
                | Q(student__school_id__icontains=search)
                | Q(receipt_number__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        fees_list = list(context["fees"])

        # Calculate dynamic KPIs
        context["kpis"] = calculate_finance_kpis(fees_list)

        # Filters and dropdown options
        context["classes"] = Classes.objects.all().order_by("grade", "section")
        context["months"] = Month.objects.all().order_by("id")
        context["years"] = AcademiceYear.objects.all().order_by("-year")

        # Determine current selected year
        current_year_id = self.request.GET.get("year_id")
        if current_year_id is None:
            y1403 = AcademiceYear.objects.filter(year=1403).first()
            if y1403:
                current_year_id = str(y1403.id)
        context["selected_year_id"] = current_year_id

        context["search"] = self.request.GET.get("search", "")
        context["selected_class_id"] = self.request.GET.get("class_id", "")
        context["selected_month_id"] = self.request.GET.get("month_id", "")
        context["selected_fee_type"] = self.request.GET.get("fee_type", "")

        # Prepare active students for the modal dropdown
        students_qs = Student.objects.filter(status__id=1).order_by("name")
        student_classes = {
            sc.student_id: sc.classs for sc in StudentClass.objects.select_related("classs").all()
        }
        students_modal = []
        for s in students_qs:
            cls = student_classes.get(s.id)
            students_modal.append({
                "id": s.id,
                "name": s.name,
                "fname": s.fname or "",
                "school_id": s.school_id or "",
                "class_id": cls.id if cls else "",
                "class_name": f"{cls.alpha_grade} - {cls.section}" if cls else "نامشخص",
            })
        context["students_for_modal"] = students_modal

        # Next receipt number suggestion
        next_num = Fee.objects.count() + 1001
        context["auto_receipt_number"] = f"REC-1403-{next_num}"
        context["today_str"] = get_current_jalali_date_str()

        return context


@is_admin
def fee_create(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        class_id = request.POST.get("class_id")
        month_id = request.POST.get("month_id")
        year_id = request.POST.get("year_id")
        amount = request.POST.get("amount") or 0
        paied = request.POST.get("paied") or 0
        payment_date_str = request.POST.get("payment_date")
        payment_method = request.POST.get(
            "payment_method") or "نقدی (صندوق مکتب)"
        fee_category = request.POST.get("fee_category") or "شهریه ماهوار"
        receipt_number = request.POST.get("receipt_number")
        notes = request.POST.get("notes") or ""

        try:
            student = get_object_or_404(Student, id=student_id)
            month = get_object_or_404(Month, id=month_id)
            year = get_object_or_404(AcademiceYear, id=year_id)

            # Detect class if not specified
            class_section = None
            if class_id and str(class_id).isdigit():
                class_section = Classes.objects.filter(
                    id=int(class_id)).first()
            if not class_section:
                sc = (StudentClass.objects.filter(student=student, academice_year=year).first()
                      or StudentClass.objects.filter(student=student).first())
                if sc:
                    class_section = sc.classs

            # Parse payment date
            if payment_date_str:
                try:
                    p_date = datetime.datetime.strptime(
                        payment_date_str, "%Y-%m-%d").date()
                except Exception:
                    p_date = datetime.date.today()
            else:
                p_date = datetime.date.today()

            if not receipt_number or not receipt_number.strip():
                receipt_number = f"REC-{year.year}-{Fee.objects.count() + 1001}"

            fee = Fee.objects.create(
                student=student,
                class_section=class_section,
                month=month,
                academice_year=year,
                amount=int(float(amount)),
                paied=int(float(paied)),
                payment_date=p_date,
                payment_method=payment_method.strip(),
                fee_category=fee_category.strip(),
                receipt_number=receipt_number.strip(),
                notes=notes.strip(),
            )
            messages.success(
                request, f"قبض پرداختی با موفقیت صادر شد. شماره رسید: {fee.receipt_number}")

            if request.POST.get("action") == "save_and_print":
                return redirect(reverse("dashboard:fee-receipt", kwargs={"id": fee.id}) + "?print=1")
            return redirect(reverse("dashboard:finance-list"))
        except Exception as e:
            messages.error(request, f"خطا در ثبت قبض پرداختی: {str(e)}")
            return redirect(reverse("dashboard:finance-list"))

    context = {
        "classes": Classes.objects.all().order_by("grade", "section"),
        "months": Month.objects.all().order_by("id"),
        "years": AcademiceYear.objects.all().order_by("-year"),
        "all_students": Student.objects.filter(status_id=1).order_by("name"),
        "is_create": True,
    }
    return render(request, "dashboard/finance/fee_edite.html", context)


@is_admin
def fee_edite(request, id):

    fee = get_object_or_404(
        Fee.objects.select_related(
            "student", "class_section", "month", "academice_year"),
        id=id
    )

    if request.method == "POST":
        class_id = request.POST.get("class_id")
        month_id = request.POST.get("month_id")
        year_id = request.POST.get("year_id")
        amount = request.POST.get("amount") or 0
        paied = request.POST.get("paied") or 0
        payment_date_str = request.POST.get("payment_date")
        payment_method = request.POST.get(
            "payment_method") or fee.payment_method
        fee_category = request.POST.get("fee_category") or fee.fee_category
        receipt_number = request.POST.get(
            "receipt_number") or fee.receipt_number
        notes = request.POST.get("notes") or ""

        try:
            if class_id and str(class_id).isdigit():
                fee.class_section_id = int(class_id)
            if month_id and str(month_id).isdigit():
                fee.month_id = int(month_id)
            if year_id and str(year_id).isdigit():
                fee.academice_year_id = int(year_id)

            fee.amount = int(float(amount))
            fee.paied = int(float(paied))

            if payment_date_str:
                try:
                    fee.payment_date = datetime.datetime.strptime(
                        payment_date_str, "%Y-%m-%d").date()
                except Exception:
                    pass

            fee.payment_method = payment_method.strip()
            fee.fee_category = fee_category.strip()
            fee.receipt_number = receipt_number.strip()
            fee.notes = notes.strip()
            fee.save()
            messages.success(
                request, f"قبض شماره {fee.receipt_number or fee.id} با موفقیت ویرایش گردید.")
            return redirect(reverse("dashboard:finance-list"))
        except Exception as e:
            messages.error(request, f"خطا در ویرایش قبض: {str(e)}")

    context = {
        "fee": fee,
        "classes": Classes.objects.all().order_by("grade", "section"),
        "months": Month.objects.all().order_by("id"),
        "years": AcademiceYear.objects.all().order_by("-year"),
        "fee_categories": ["شهریه ماهوار", "فیس داخله", "ترانسپورت", "کتاب و قرطاسیه", "لباس فرم", "متفرقه"],
        "payment_methods": ["نقدی (صندوق مکتب)", "واریز به حساب بانکی", "حواله صرافی"],
    }
    return render(request, "dashboard/finance/fee_edite.html", context)


@is_admin
def fee_delete(request, id):

    fee = get_object_or_404(Fee, id=id)
    receipt_num = fee.receipt_number or str(fee.id)
    student_name = fee.student.name if fee.student else ""
    fee.delete()
    messages.success(
        request, f"قبض شماره {receipt_num} متعلق به شاگرد «{student_name}» با موفقیت حذف گردید.")
    return redirect(reverse("dashboard:finance-list"))


@is_admin
def fee_receipt_view(request, id):

    fee = get_object_or_404(
        Fee.objects.select_related(
            "student", "class_section", "month", "academice_year"),
        id=id
    )
    paied_words = number_to_dari_words(fee.paied or 0)
    amount_words = number_to_dari_words(fee.amount or 0)
    remaining = fee.remaining
    remaining_words = number_to_dari_words(
        remaining) if remaining > 0 else "صفر افغانی"
    auto_print = request.GET.get("print") == "1"

    context = {
        "fee": fee,
        "paied_words": paied_words,
        "amount_words": amount_words,
        "remaining": remaining,
        "remaining_words": remaining_words,
        "auto_print": auto_print,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/finance/fee_receipt.html", context)


@is_admin
def expenses_view(request):

    if request.method == "POST":
        category = request.POST.get("category") or "متفرقه"
        title = request.POST.get("title") or "هزینه مکتب"
        amount = request.POST.get("amount") or 0
        payment_date_str = request.POST.get("payment_date")
        recipient = request.POST.get("recipient") or ""
        receipt_number = request.POST.get("receipt_number") or ""
        payment_method = request.POST.get("payment_method") or "نقدی"
        year_id = request.POST.get("year_id")
        month_id = request.POST.get("month_id")
        notes = request.POST.get("notes") or ""

        try:
            if payment_date_str:
                try:
                    p_date = datetime.datetime.strptime(
                        payment_date_str, "%Y-%m-%d").date()
                except Exception:
                    p_date = datetime.date.today()
            else:
                p_date = datetime.date.today()

            year = AcademiceYear.objects.filter(id=year_id).first(
            ) if year_id else AcademiceYear.objects.first()
            month = Month.objects.filter(
                id=month_id).first() if month_id else None

            if not receipt_number:
                receipt_number = f"EXP-{year.year if year else '1403'}-{Expense.objects.count() + 501}"

            expense = Expense.objects.create(
                category=category.strip(),
                title=title.strip(),
                amount=int(float(amount)),
                payment_date=p_date,
                recipient=recipient.strip(),
                receipt_number=receipt_number.strip(),
                payment_method=payment_method.strip(),
                academice_year=year,
                month=month,
                notes=notes.strip(),
            )
            messages.success(
                request, f"سند هزینه «{expense.title}» با شماره {expense.receipt_number} با موفقیت ثبت شد.")
            return redirect(reverse("dashboard:finance-expenses"))
        except Exception as e:
            messages.error(request, f"خطا در ثبت هزینه: {str(e)}")
            return redirect(reverse("dashboard:finance-expenses"))

    # GET filter
    qs = Expense.objects.select_related(
        "academice_year", "month").order_by("-payment_date", "-id")
    year_id = request.GET.get("year_id")
    month_id = request.GET.get("month_id")
    category = request.GET.get("category")
    search = request.GET.get("search")

    if year_id and year_id != "all":
        if str(year_id).isdigit():
            qs = qs.filter(academice_year_id=int(year_id))
    elif year_id is None:
        y1403 = AcademiceYear.objects.filter(year=1403).first()
        if y1403:
            qs = qs.filter(academice_year=y1403)
            year_id = str(y1403.id)

    if month_id and str(month_id).isdigit():
        qs = qs.filter(month_id=int(month_id))
    if category and category != "all":
        qs = qs.filter(category=category)
    if search:
        search = search.strip()
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(recipient__icontains=search)
            | Q(receipt_number__icontains=search)
            | Q(notes__icontains=search)
        )

    expenses_list = list(qs)
    total_expenses = sum(e.amount or 0 for e in expenses_list)
    salaries_total = sum(
        e.amount or 0 for e in expenses_list if "معاش" in (e.category or ""))
    rent_utilities_total = sum(e.amount or 0 for e in expenses_list if (
        "کرایه" in (e.category or "") or "برق" in (e.category or "")))
    supplies_total = sum(e.amount or 0 for e in expenses_list if (
        "قرطاسیه" in (e.category or "") or "ترمیم" in (e.category or "")))

    expense_categories = [
        "معاشات استادان و پرسونل",
        "کرایه تعمیر مکتب",
        "برق، آب و انترنت",
        "قرطاسیه، چاپ و مواد درسی",
        "تعمیرات، حفظ و مراقبت",
        "تجهیزات و فناوری",
        "مصارف پذیرایی و اداری",
        "متفرقه"
    ]

    context = {
        "expenses": expenses_list,
        "total_expenses": total_expenses,
        "salaries_total": salaries_total,
        "rent_utilities_total": rent_utilities_total,
        "supplies_total": supplies_total,
        "expenses_count": len(expenses_list),
        "expense_categories": expense_categories,
        "months": Month.objects.all().order_by("id"),
        "years": AcademiceYear.objects.all().order_by("-year"),
        "selected_year_id": year_id,
        "selected_month_id": month_id,
        "selected_category": category,
        "search": search,
        "auto_receipt_number": f"EXP-1403-{Expense.objects.count() + 501}",
    }
    return render(request, "dashboard/finance/expenses.html", context)


@is_admin
def expense_delete(request, id):
    expense = get_object_or_404(Expense, id=id)
    title = expense.title
    receipt_num = expense.receipt_number or str(expense.id)
    expense.delete()
    messages.success(
        request, f"سند هزینه «{title}» ({receipt_num}) با موفقیت حذف گردید.")
    return redirect(reverse("dashboard:finance-expenses"))


@is_admin
def finance_report_view(request):
    year_id = request.GET.get("year_id")
    years = AcademiceYear.objects.all().order_by("-year")

    if year_id and str(year_id).isdigit():
        selected_year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        selected_year = AcademiceYear.objects.filter(
            year=1403).first() or years.first()

    report = calculate_financial_report(selected_year)

    context = {
        "report": report,
        "years": years,
        "selected_year": selected_year,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/finance/finance_report.html", context)


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Timetable & Schedule Management SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

@is_admin
def timetable_class_view(request):
    years = AcademiceYear.objects.all().order_by("-year")
    classes = Classes.objects.all().order_by("grade", "section")

    year_id = request.GET.get("year_id")
    class_id = request.GET.get("class_id")

    if year_id and str(year_id).isdigit():
        selected_year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        selected_year = AcademiceYear.objects.filter(
            year=1403).first() or years.first()

    if class_id and str(class_id).isdigit():
        selected_class = Classes.objects.filter(id=int(class_id)).first()
    else:
        selected_class = (
            Classes.objects.filter(alpha_grade="دهم", section="الف").first()
            or classes.first()
        )

    matrix_data = {}
    class_subjects = []
    if selected_class and selected_year:
        matrix_data = get_class_timetable_matrix(
            selected_class.id, selected_year.id)
        class_subjects = list(selected_class.subjects.all().order_by("name"))
        if not class_subjects:
            class_subjects = list(Subject.objects.all().order_by("name"))

    active_teachers = Teacher.objects.filter(status__id=1).order_by("name")

    context = {
        "selected_class": selected_class,
        "selected_year": selected_year,
        "classes": classes,
        "years": years,
        "matrix": matrix_data,
        "class_subjects": class_subjects,
        "teachers": active_teachers,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/timetable/class_timetable.html", context)


@is_admin
def timetable_teacher_view(request):
    """
    Weekly Timetable view for a specific Teacher (تقسیم اوقات کاری استاد).
    """
    years = AcademiceYear.objects.all().order_by("-year")
    teachers = Teacher.objects.filter(status__id=1).order_by("name")
    classes = Classes.objects.all().order_by("grade", "section")
    subjects = Subject.objects.all().order_by("name")

    year_id = request.GET.get("year_id")
    teacher_id = request.GET.get("teacher_id")

    if year_id and str(year_id).isdigit():
        selected_year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        selected_year = AcademiceYear.objects.filter(
            year=1403).first() or years.first()

    if teacher_id and str(teacher_id).isdigit():
        selected_teacher = Teacher.objects.filter(id=int(teacher_id)).first()
    else:
        selected_teacher = teachers.first()

    matrix_data = {}
    if selected_teacher and selected_year:
        matrix_data = get_teacher_timetable_matrix(
            selected_teacher.id, selected_year.id)

    context = {
        "selected_teacher": selected_teacher,
        "selected_year": selected_year,
        "teachers": teachers,
        "years": years,
        "classes": classes,
        "subjects": subjects,
        "matrix": matrix_data,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/timetable/teacher_timetable.html", context)


@is_admin
def timetable_master_view(request):
    """
    Master School Schedule Matrix across all classes (جدول عمومی تقسیم اوقات مکتب).
    """
    years = AcademiceYear.objects.all().order_by("-year")
    year_id = request.GET.get("year_id")
    day_num = request.GET.get("day", 1)

    try:
        day_num = int(day_num)
        if day_num < 1 or day_num > 6:
            day_num = 1
    except (ValueError, TypeError):
        day_num = 1

    if year_id and str(year_id).isdigit():
        selected_year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        selected_year = AcademiceYear.objects.filter(
            year=1403).first() or years.first()

    matrix_data = get_master_timetable_matrix(selected_year.id, day_num)

    context = {
        "matrix": matrix_data,
        "selected_day_num": day_num,
        "selected_year": selected_year,
        "years": years,
        "days": DAYS,
        "periods": PERIODS,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/timetable/master_timetable.html", context)


@is_admin
def timetable_slot_save(request):
    """
    Save or update a timetable slot with conflict checking.
    """
    if request.method == "POST":
        class_id = request.POST.get("class_id")
        teacher_id = request.POST.get("teacher_id")
        subject_id = request.POST.get("subject_id")
        day_of_week = request.POST.get("day_of_week")
        period = request.POST.get("period")
        year_id = request.POST.get("year_id")
        room_number = request.POST.get("room_number") or "اتاق صنف"
        notes = request.POST.get("notes") or ""
        slot_id = request.POST.get("slot_id")
        redirect_to = request.POST.get("redirect_to", "class")

        try:
            class_id = int(class_id)
            teacher_id = int(teacher_id)
            subject_id = int(subject_id)
            day_of_week = int(day_of_week)
            period = int(period)
            year_id = int(year_id)
            exclude_id = int(slot_id) if slot_id and str(
                slot_id).isdigit() else None

            # Validate conflicts
            is_valid, conflict_msg = validate_timetable_slot(
                class_id=class_id,
                teacher_id=teacher_id,
                day_of_week=day_of_week,
                period=period,
                academic_year_id=year_id,
                exclude_slot_id=exclude_id,
            )

            if not is_valid:
                messages.error(request, conflict_msg)
            else:
                cls_obj = get_object_or_404(Classes, id=class_id)
                teacher_obj = get_object_or_404(Teacher, id=teacher_id)
                subject_obj = get_object_or_404(Subject, id=subject_id)
                year_obj = get_object_or_404(AcademiceYear, id=year_id)

                if exclude_id:
                    slot = get_object_or_404(TimeTable, id=exclude_id)
                    slot.classs = cls_obj
                    slot.teacher = teacher_obj
                    slot.subject = subject_obj
                    slot.day_of_week = day_of_week
                    slot.period = period
                    slot.academic_year = year_obj
                    slot.room_number = room_number.strip()
                    slot.notes = notes.strip()
                    slot.save()
                    messages.success(
                        request, f"ساعت درسی {slot.day_name} ({slot.period_name}) با موفقیت به‌روزرسانی شد.")
                else:
                    slot, created = TimeTable.objects.update_or_create(
                        classs=cls_obj,
                        day_of_week=day_of_week,
                        period=period,
                        academic_year=year_obj,
                        defaults={
                            "teacher": teacher_obj,
                            "subject": subject_obj,
                            "room_number": room_number.strip(),
                            "notes": notes.strip(),
                        }
                    )
                    messages.success(
                        request, f"ساعت درسی برای روز {slot.day_name} ({slot.period_name}) با موفقیت ثبت شد.")

        except Exception as e:
            messages.error(request, f"خطا در ثبت ساعت درسی: {str(e)}")

        if redirect_to == "teacher":
            return redirect(f"{reverse('dashboard:timetable-teacher')}?teacher_id={teacher_id}&year_id={year_id}")
        return redirect(f"{reverse('dashboard:timetable-class')}?class_id={class_id}&year_id={year_id}")

    return redirect(reverse("dashboard:timetable-class"))


@is_admin
def timetable_slot_delete(request, id):
    """
    Delete a timetable slot.
    """
    slot = get_object_or_404(TimeTable, id=id)
    class_id = slot.classs_id
    teacher_id = slot.teacher_id
    year_id = slot.academic_year_id
    day_name = slot.day_name
    period_name = slot.period_name
    redirect_to = request.GET.get("redirect_to", "class")

    slot.delete()
    messages.success(
        request, f"ساعت درسی {day_name} ({period_name}) با موفقیت حذف گردید.")

    if redirect_to == "teacher":
        return redirect(f"{reverse('dashboard:timetable-teacher')}?teacher_id={teacher_id}&year_id={year_id}")
    return redirect(f"{reverse('dashboard:timetable-class')}?class_id={class_id}&year_id={year_id}")


@is_admin
def timetable_class_print(request, class_id):
    """
    Official Afghan Wall Timetable for Classroom (تقسیم اوقات دیواری صنف) - A4 Landscape Print.
    """
    cls = get_object_or_404(Classes.objects.select_related(
        "guidence", "academice_year"), id=class_id)
    year_id = request.GET.get("year_id")
    if year_id and str(year_id).isdigit():
        year = AcademiceYear.objects.filter(
            id=int(year_id)).first() or cls.academice_year
    else:
        year = cls.academice_year or AcademiceYear.objects.filter(
            year=1403).first() or AcademiceYear.objects.first()

    matrix_data = get_class_timetable_matrix(cls.id, year.id)

    context = {
        "cls": cls,
        "year": year,
        "matrix": matrix_data,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/timetable/class_timetable_print.html", context)


@is_admin
def timetable_teacher_print(request, teacher_id):
    """
    Official Teacher Timetable Schedule Card (کارت تقسیم اوقات کاری استاد) - A4 Print.
    """
    teacher = get_object_or_404(Teacher, id=teacher_id)
    year_id = request.GET.get("year_id")
    if year_id and str(year_id).isdigit():
        year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        year = AcademiceYear.objects.filter(
            year=1403).first() or AcademiceYear.objects.first()

    matrix_data = get_teacher_timetable_matrix(teacher.id, year.id)

    context = {
        "teacher": teacher,
        "year": year,
        "matrix": matrix_data,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/timetable/teacher_timetable_print.html", context)


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Subject & Afghan Curriculum Management SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

@is_admin
def subject_list_view(request):
    """
    Academic Curriculum & Subject Directory (فهرست مضامین و مدیریت نصاب تعلیمی معارف).
    """
    qs = Subject.objects.prefetch_related("classes").all()

    search_query = request.GET.get("search", "").strip()
    category_filter = request.GET.get("category", "").strip()
    level_filter = request.GET.get("level", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search_query:
        qs = qs.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        qs = qs.filter(category=category_filter)

    if level_filter:
        qs = qs.filter(educational_level=level_filter)

    if status_filter == "active":
        qs = qs.filter(is_active=True)
    elif status_filter == "inactive":
        qs = qs.filter(is_active=False)

    subjects = qs.order_by("category", "name")
    stats = get_subject_statistics()
    classes = Classes.objects.all().order_by("grade", "section")

    context = {
        "subjects": subjects,
        "stats": stats,
        "classes": classes,
        "categories": Subject.CATEGORY_CHOICES,
        "levels": Subject.LEVEL_CHOICES,
        "search_query": search_query,
        "selected_category": category_filter,
        "selected_level": level_filter,
        "selected_status": status_filter,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/subjects/subject_list.html", context)


@is_admin
def subject_create_view(request):
    """
    Create a new curriculum subject (تعریف مضمون رسمی جدید در نصاب تعلیمی).
    """
    classes = Classes.objects.all().order_by("grade", "section")
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(
                request,
                f"مضمون رسمی «{subject.name}» ({subject.code or 'بدون کد'}) با موفقیت در نصاب تعلیمی مکتب ثبت گردید."
            )
            return redirect(reverse("dashboard:subject-list"))
        else:
            messages.error(
                request, "لطفاً خطاهای فرم ثبت مضمون را بررسی و اصلاح فرمایید.")
    else:
        form = SubjectForm()

    context = {
        "form": form,
        "classes": classes,
        "is_create": True,
        "categories": Subject.CATEGORY_CHOICES,
        "levels": Subject.LEVEL_CHOICES,
    }
    return render(request, "dashboard/subjects/subject_form.html", context)


@is_admin
def subject_edit_view(request, id):
    """
    Edit curriculum subject details (ویرایش و اصلاح مشخصات مضمون تعلیمی).
    """
    subject = get_object_or_404(Subject, id=id)
    classes = Classes.objects.all().order_by("grade", "section")

    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(
                request,
                f"مشخصات مضمون «{subject.name}» با موفقیت به‌روزرسانی و ذخیره شد."
            )
            return redirect(reverse("dashboard:subject-list"))
        else:
            messages.error(
                request, "لطفاً خطاهای فرم ویرایش مضمون را بررسی فرمایید.")
    else:
        form = SubjectForm(instance=subject)

    context = {
        "form": form,
        "subject": subject,
        "classes": classes,
        "is_create": False,
        "categories": Subject.CATEGORY_CHOICES,
        "levels": Subject.LEVEL_CHOICES,
    }
    return render(request, "dashboard/subjects/subject_form.html", context)


@is_admin
def subject_detail_view(request, id):
    """
    Detailed Profile of an Academic Subject (مشخصات و آمار تحلیلی مضمون).
    """
    subject = get_object_or_404(Subject, id=id)
    metrics = get_subject_detail_metrics(subject)
    validation = validate_subject_deletion(subject)

    context = {
        "subject": subject,
        "metrics": metrics,
        "validation": validation,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/subjects/subject_detail.html", context)


@is_admin
def subject_toggle_status_view(request, id):
    """
    Toggle Active / Inactive status of a subject (فعال / غیرفعال‌سازی در نصاب).
    """
    subject = get_object_or_404(Subject, id=id)
    subject.is_active = not subject.is_active
    subject.save()

    status_str = "فعال" if subject.is_active else "غیرفعال"
    messages.success(
        request,
        f"وضعیت مضمون «{subject.name}» با موفقیت به «{status_str}» تغییر یافت."
    )
    return redirect(reverse("dashboard:subject-list"))


@is_admin
def subject_delete_view(request, id):
    """
    Safe Deletion of a Subject with Integrity Protection (حذف ایمن مضمون).
    """
    subject = get_object_or_404(Subject, id=id)
    validation = validate_subject_deletion(subject)

    if not validation["can_delete"]:
        messages.warning(request, validation["reason"])
        return redirect(reverse("dashboard:subject-list"))

    subj_name = subject.name
    subject.delete()
    messages.success(
        request, f"مضمون «{subj_name}» با موفقیت از سیستم حذف گردید.")
    return redirect(reverse("dashboard:subject-list"))


@is_admin
def subject_class_matrix_view(request):
    """
    Class Curriculum Assignment Matrix & Bulk Afghan MoE Standards Application
    (ماتریس تخصیص مضامین به صنوف و اِعمال نصاب معیاری وزارت معارف).
    """
    classes = Classes.objects.all().order_by("grade", "section")
    all_subjects = Subject.objects.all().order_by("category", "name")

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    if request.method == "POST" and selected_class:
        action_type = request.POST.get("action_type")

        if action_type == "apply_standard":
            stage = request.POST.get(
                "curriculum_stage") or get_class_educational_stage(selected_class)
            result = apply_afghan_curriculum_to_class(selected_class, stage)
            messages.success(
                request,
                f"نصاب تعلیمی رسمی وزارت معارف (دوره {stage}) برای صنف {selected_class.alpha_grade} شعبه {selected_class.section} با موفقیت اعمال گردید ({result['assigned_count']} مضمون)."
            )
            return redirect(f"{reverse('dashboard:subject-class-matrix')}?class_id={selected_class.id}")

        elif action_type == "save_custom":
            selected_subject_ids = request.POST.getlist("subject_ids")
            selected_class.subjects.set(selected_subject_ids)
            messages.success(
                request,
                f"مضامین اختصاصی صنف {selected_class.alpha_grade} شعبه {selected_class.section} با موفقیت ذخیره شد ({len(selected_subject_ids)} مضمون)."
            )
            return redirect(f"{reverse('dashboard:subject-class-matrix')}?class_id={selected_class.id}")

    current_assigned_ids = set(selected_class.subjects.values_list(
        "id", flat=True)) if selected_class else set()
    current_weekly_hours = sum(
        s.weekly_hours for s in selected_class.subjects.all()) if selected_class else 0
    educational_stage = get_class_educational_stage(
        selected_class) if selected_class else "لیسه"

    # Group subjects by category for organized display
    subjects_by_category = {}
    for s in all_subjects:
        cat = s.category or "سایر مضامین"
        if cat not in subjects_by_category:
            subjects_by_category[cat] = []
        subjects_by_category[cat].append(s)

    context = {
        "classes": classes,
        "selected_class": selected_class,
        "all_subjects": all_subjects,
        "subjects_by_category": subjects_by_category,
        "current_assigned_ids": current_assigned_ids,
        "current_weekly_hours": current_weekly_hours,
        "educational_stage": educational_stage,
        "standards": get_afghan_curriculum_standards(),
    }
    return render(request, "dashboard/subjects/class_matrix.html", context)


@is_admin
def subject_class_print_view(request, class_id):
    """
    Official Class Curriculum & Syllabus Sheet (مفردات و جدول مضامین رسمی صنف) - A4 Print Layout.
    """
    cls = get_object_or_404(Classes, id=class_id)
    year_id = request.GET.get("year_id")
    if year_id and str(year_id).isdigit():
        year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        year = AcademiceYear.objects.filter(
            year=1403).first() or AcademiceYear.objects.first()

    subjects = list(cls.subjects.all().order_by("category", "name"))
    total_hours = sum(s.weekly_hours for s in subjects)

    # Attach teacher info from TimeTable or TeacherSubject
    subject_rows = []
    for s in subjects:
        tt_slot = TimeTable.objects.filter(classs=cls, subject=s).first()
        ts_rec = TeacherSubject.objects.filter(classs=cls, subject=s).first()
        teacher = tt_slot.teacher if tt_slot else (
            ts_rec.teacher if ts_rec else None)
        subject_rows.append({
            "subject": s,
            "teacher": teacher,
            "weekly_hours": s.weekly_hours,
        })

    context = {
        "cls": cls,
        "year": year,
        "subjects": subjects,
        "subject_rows": subject_rows,
        "total_subjects": len(subjects),
        "total_hours": total_hours,
        "educational_stage": get_class_educational_stage(cls),
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/subjects/class_curriculum_print.html", context)


# -----------------------------------------------------------------------------
#####
#####
######### -------------- Teacher Portal & Workflow SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

def is_teacher_or_admin(func):
    """
    Security decorator allowing access to Teachers and Administrators.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        if request.user.is_staff or (hasattr(request.user, "teacher_profile") and request.user.teacher_profile):
            return func(request, *args, **kwargs)
        messages.error(request, "شما دسترسی لازم به پورتال اساتید را ندارید.")
        return redirect(reverse("accounts:login"))
    return wrapper


@is_teacher_or_admin
def teacher_portal_view(request):
    """
    Main Teacher Dashboard (داشبورد و پورتال اختصاصی استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        messages.warning(
            request, "حساب استادی فعالی یافت نشد. لطفاً ابتدا یک استاد را انتخاب نمایید.")
        return redirect(reverse("dashboard:admin-dashboard"))

    years = AcademiceYear.objects.all().order_by("-year")
    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or years.first()

    kpis = get_teacher_kpis(teacher, academic_year)
    today_schedule = get_teacher_today_schedule(teacher, academic_year.id)
    assigned_classes = get_teacher_assigned_classes(teacher)
    assigned_subjects = get_teacher_assigned_subjects(teacher)

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "kpis": kpis,
        "today_schedule": today_schedule,
        "assigned_classes": assigned_classes,
        "assigned_subjects": assigned_subjects,
        "all_teachers": all_teachers,
        "academic_year": academic_year,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/portal.html", context)


@is_teacher_or_admin
def teacher_attendance_view(request):
    """
    Class Attendance Management for Teachers (ثبت و مدیریت حاضری صنف توسط استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("dashboard:teacher-portal"))

    assigned_classes = get_teacher_assigned_classes(teacher)
    guidance_class = Classes.objects.filter(guidence=teacher).first()

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(
            id=int(selected_class_id)).first()
    else:
        selected_class = guidance_class or (
            assigned_classes[0] if assigned_classes else None)

    months = Month.objects.all().order_by("id")
    selected_month_id = request.GET.get(
        "month_id") or request.POST.get("month_id")
    if selected_month_id and str(selected_month_id).isdigit():
        selected_month = Month.objects.filter(
            id=int(selected_month_id)).first()
    else:
        selected_month = months.first()

    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or AcademiceYear.objects.first()

    default_all_days = 24

    if request.method == "POST" and selected_class and selected_month:
        all_days = int(request.POST.get("all_days", default_all_days or 24))
        enrollments = StudentClass.objects.filter(
            classs=selected_class, academice_year=academic_year
        ).select_related("student")

        saved_count = 0
        for sc in enrollments:
            std = sc.student
            p_val = request.POST.get(f"present_{std.id}")
            a_val = request.POST.get(f"absent_{std.id}")
            s_val = request.POST.get(f"sick_{std.id}")
            e_val = request.POST.get(f"excused_{std.id}")

            if p_val is not None:
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
                    student=std,
                    classs=selected_class,
                    month=selected_month,
                    academice_year=academic_year,
                    defaults={
                        "alldays": all_days,
                        "present": present,
                        "absent": absent,
                        "sick": sick,
                        "excused": excused,
                    }
                )
                saved_count += 1

        messages.success(
            request,
            f"کارنامه حاضری صنف {selected_class.alpha_grade} برای ماه {selected_month.name} با موفقیت ({saved_count} شاگرد) ذخیره شد."
        )
        return redirect(f"{reverse('dashboard:teacher-attendance')}?class_id={selected_class.id}&month_id={selected_month.id}")

    # Prepare student rows for GET
    student_rows = []
    if selected_class and selected_month:
        enrollments = (
            StudentClass.objects.filter(
                classs=selected_class, academice_year=academic_year)
            .select_related("student")
            .order_by("student__name")
        )
        existing_map = {
            att.student_id: att
            for att in Attendance.objects.filter(
                classs=selected_class, month=selected_month, academice_year=academic_year
            )
        }
        for sc in enrollments:
            std = sc.student
            att = existing_map.get(std.id)
            if att:
                default_all_days = att.alldays
            student_rows.append({
                "student": std,
                "att": att,
                "present": att.present if att else default_all_days,
                "absent": att.absent if att else 0,
                "sick": att.sick if att else 0,
                "excused": att.excused if att else 0,
                "percent": att.get_present_percentage() if att else 100,
            })

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "assigned_classes": assigned_classes,
        "selected_class": selected_class,
        "guidance_class": guidance_class,
        "months": months,
        "selected_month": selected_month,
        "academic_year": academic_year,
        "default_all_days": default_all_days,
        "student_rows": student_rows,
        "all_teachers": all_teachers,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/attendance.html", context)


@is_teacher_or_admin
def teacher_assessment_view(request):
    """
    Monthly Assessment Entry for Teacher's Subjects (ثبت ارزیابی‌های ماهوار مضامین استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("dashboard:teacher-portal"))

    assigned_classes = get_teacher_assigned_classes(teacher)

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(
            id=int(selected_class_id)).first()
    else:
        selected_class = assigned_classes[0] if assigned_classes else None

    assigned_subjects = get_teacher_assigned_subjects(teacher, selected_class)
    selected_subject_id = request.GET.get(
        "subject_id") or request.POST.get("subject_id")
    if selected_subject_id and str(selected_subject_id).isdigit():
        selected_subject = Subject.objects.filter(
            id=int(selected_subject_id)).first()
    else:
        selected_subject = assigned_subjects[0] if assigned_subjects else None

    months = Month.objects.all().order_by("id")
    selected_month_id = request.GET.get(
        "month_id") or request.POST.get("month_id")
    if selected_month_id and str(selected_month_id).isdigit():
        selected_month = Month.objects.filter(
            id=int(selected_month_id)).first()
    else:
        selected_month = months.first()

    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or AcademiceYear.objects.first()

    default_max_score = 100

    if request.method == "POST" and selected_class and selected_subject and selected_month:
        enrollments = StudentClass.objects.filter(
            classs=selected_class, academice_year=academic_year
        ).select_related("student")

        saved_count = 0
        for sc in enrollments:
            std = sc.student
            score_key = f"score_{std.id}"
            max_key = f"max_{std.id}"

            if score_key in request.POST:
                raw_score = request.POST.get(score_key, "").strip()
                raw_max = request.POST.get(max_key, default_max_score)

                if raw_score != "":
                    try:
                        score = int(raw_score)
                        max_sc = max(1, int(raw_max or default_max_score))
                    except (ValueError, TypeError):
                        score = 0
                        max_sc = default_max_score

                    Assessment.objects.update_or_create(
                        student=std,
                        classs=selected_class,
                        subject=selected_subject,
                        month=selected_month,
                        academice_year=academic_year,
                        defaults={
                            "teacher": teacher,
                            "score": score,
                            "max_score": max_sc,
                        }
                    )
                    saved_count += 1

        messages.success(
            request,
            f"نمرات ارزیابی ماه {selected_month.name} مضمون «{selected_subject.name}» برای صنف {selected_class.alpha_grade} با موفقیت ({saved_count} شاگرد) ذخیره شد."
        )
        return redirect(f"{reverse('dashboard:teacher-assessment')}?class_id={selected_class.id}&subject_id={selected_subject.id}&month_id={selected_month.id}")

    # Prepare student rows for GET
    student_rows = []
    if selected_class and selected_subject and selected_month:
        enrollments = (
            StudentClass.objects.filter(
                classs=selected_class, academice_year=academic_year)
            .select_related("student")
            .order_by("student__name")
        )
        existing_map = {
            ass.student_id: ass
            for ass in Assessment.objects.filter(
                classs=selected_class,
                subject=selected_subject,
                month=selected_month,
                academice_year=academic_year
            )
        }
        for sc in enrollments:
            std = sc.student
            ass = existing_map.get(std.id)
            student_rows.append({
                "student": std,
                "score": ass.score if ass else "",
                "max_score": ass.max_score if ass else default_max_score,
                "has_record": ass is not None,
                "percent": ass.getPercentage() if ass else 0,
            })

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "assigned_classes": assigned_classes,
        "selected_class": selected_class,
        "assigned_subjects": assigned_subjects,
        "selected_subject": selected_subject,
        "months": months,
        "selected_month": selected_month,
        "academic_year": academic_year,
        "student_rows": student_rows,
        "all_teachers": all_teachers,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/assessment.html", context)


@is_teacher_or_admin
def teacher_shaqqa_view(request):
    """
    Digital Shaqqa & Exam Marks Entry for Teacher's Subjects
    (ورود نمرات شقه امتحانات چهارونیم ماهه و سالانه مطابق طرزالعمل معارف).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("dashboard:teacher-portal"))

    assigned_classes = get_teacher_assigned_classes(teacher)

    selected_class_id = request.GET.get(
        "class_id") or request.POST.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(
            id=int(selected_class_id)).first()
    else:
        selected_class = assigned_classes[0] if assigned_classes else None

    assigned_subjects = get_teacher_assigned_subjects(teacher, selected_class)
    selected_subject_id = request.GET.get(
        "subject_id") or request.POST.get("subject_id")
    if selected_subject_id and str(selected_subject_id).isdigit():
        selected_subject = Subject.objects.filter(
            id=int(selected_subject_id)).first()
    else:
        selected_subject = assigned_subjects[0] if assigned_subjects else None

    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or AcademiceYear.objects.first()

    if request.method == "POST" and selected_class and selected_subject:
        saved_count = save_teacher_shaqqa_matrix(
            teacher, selected_class, selected_subject, academic_year, request.POST
        )
        messages.success(
            request,
            f"شقه نمرات امتحان مضمون «{selected_subject.name}» برای صنف {selected_class.alpha_grade} شعبه {selected_class.section} با موفقیت ({saved_count} شاگرد) در سیستم امتحانات معارف ذخیره گردید."
        )
        return redirect(f"{reverse('dashboard:teacher-shaqqa')}?class_id={selected_class.id}&subject_id={selected_subject.id}")

    matrix_data = None
    if selected_class and selected_subject:
        matrix_data = get_teacher_shaqqa_matrix(
            teacher, selected_class, selected_subject, academic_year)

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "assigned_classes": assigned_classes,
        "selected_class": selected_class,
        "assigned_subjects": assigned_subjects,
        "selected_subject": selected_subject,
        "academic_year": academic_year,
        "matrix": matrix_data,
        "all_teachers": all_teachers,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/shaqqa.html", context)


@is_teacher_or_admin
def teacher_my_timetable_view(request):
    """
    Teacher's Personal Weekly Timetable (تقسیم اوقات تدریس هفتگی استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("dashboard:teacher-portal"))

    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or AcademiceYear.objects.first()
    matrix_data = get_teacher_timetable_matrix(teacher.id, academic_year.id)

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "matrix": matrix_data,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "academic_year": academic_year,
        "all_teachers": all_teachers,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/my_timetable.html", context)


@is_teacher_or_admin
def teacher_class_timetable_view(request):
    """
    Weekly Timetable of Teacher's Guided Class (تقسیم اوقات صنف تحت نگران استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("dashboard:teacher-portal"))

    assigned_classes = get_teacher_assigned_classes(teacher)
    guidance_class = Classes.objects.filter(guidence=teacher).first()

    selected_class_id = request.GET.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(
            id=int(selected_class_id)).first()
    else:
        selected_class = guidance_class or (
            assigned_classes[0] if assigned_classes else None)

    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or AcademiceYear.objects.first()

    matrix_data = None
    if selected_class:
        matrix_data = get_class_timetable_matrix(
            selected_class.id, academic_year.id)

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "selected_class": selected_class,
        "guidance_class": guidance_class,
        "assigned_classes": assigned_classes,
        "matrix": matrix_data,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "academic_year": academic_year,
        "all_teachers": all_teachers,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/class_timetable.html", context)


@is_teacher_or_admin
def teacher_students_view(request):
    """
    Student Roster for Teacher's Classes (لیست شاگردان صنوف استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("dashboard:teacher-portal"))

    assigned_classes = get_teacher_assigned_classes(teacher)
    selected_class_id = request.GET.get("class_id")
    search_query = request.GET.get("search", "").strip()

    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(
            id=int(selected_class_id)).first()
    else:
        selected_class = None

    academic_year = AcademiceYear.objects.filter(
        year=1403).first() or AcademiceYear.objects.first()

    enrollments_qs = StudentClass.objects.filter(
        academice_year=academic_year).select_related("student", "classs")

    if selected_class:
        enrollments_qs = enrollments_qs.filter(classs=selected_class)
    else:
        enrollments_qs = enrollments_qs.filter(classs__in=assigned_classes)

    if search_query:
        enrollments_qs = enrollments_qs.filter(
            Q(student__name__icontains=search_query) |
            Q(student__fname__icontains=search_query) |
            Q(student__school_id__icontains=search_query)
        )

    students = [sc.student for sc in enrollments_qs.order_by(
        "classs__grade", "classs__section", "student__name")]

    all_teachers = Teacher.objects.filter(status_id=1).order_by(
        "name") if request.user.is_staff else []

    context = {
        "teacher": teacher,
        "assigned_classes": assigned_classes,
        "selected_class": selected_class,
        "students": students,
        "search_query": search_query,
        "all_teachers": all_teachers,
        "academic_year": academic_year,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "dashboard/teacher/students.html", context)
