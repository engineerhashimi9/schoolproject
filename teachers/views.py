import datetime
import jdatetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from dashboard.models import (
    Teacher,
    Classes,
    Subject,
    Student,
    StudentClass,
    Attendance,
    Assessment,
    ExamMark,
    Month,
    AcademiceYear,
)
from dashboard.services.timetable_service import (
    DAYS,
    PERIODS,
    RECESS_INFO,
    get_teacher_timetable_matrix,
    get_class_timetable_matrix,
)
from .services import (
    get_current_teacher_profile,
    get_teacher_assigned_classes,
    get_teacher_assigned_subjects,
    get_teacher_today_schedule,
    get_teacher_kpis,
    get_teacher_shaqqa_matrix,
    save_teacher_shaqqa_matrix,
)


from core.utils import get_current_jalali_date_str


def teacher_access_required(func):
    """
    Security decorator: Allows access to authenticated Teachers and Administrators.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        if request.user.is_staff or (hasattr(request.user, "teacher_profile") and request.user.teacher_profile):
            return func(request, *args, **kwargs)
        messages.error(request, "شما دسترسی لازم به پورتال اساتید را ندارید.")
        return redirect(reverse("accounts:login"))
    return wrapper


@teacher_access_required
def teacher_dashboard_view(request):
    """
    Main Teacher Dashboard (داشبورد و کارتابل اختصاصی استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        messages.warning(request, "حساب استادی فعالی یافت نشد. لطفاً ابتدا یک استاد را انتخاب نمایید.")
        if request.user.is_staff:
            return redirect(reverse("dashboard:admin-dashboard"))
        return redirect(reverse("accounts:login"))

    years = AcademiceYear.objects.all().order_by("-year")
    academic_year = AcademiceYear.objects.filter(year=1403).first() or years.first()

    kpis = get_teacher_kpis(teacher, academic_year)
    today_schedule = get_teacher_today_schedule(teacher, academic_year.id if academic_year else None)
    assigned_classes = get_teacher_assigned_classes(teacher)
    assigned_subjects = get_teacher_assigned_subjects(teacher)

    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/dashboard.html", context)


@teacher_access_required
def teacher_attendance_view(request):
    """
    Class Attendance Management for Teachers (ثبت و مدیریت کارنامه حاضری صنف).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    assigned_classes = get_teacher_assigned_classes(teacher)
    guidance_class = Classes.objects.filter(guidence=teacher).first()

    selected_class_id = request.GET.get("class_id") or request.POST.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        selected_class = guidance_class or (assigned_classes[0] if assigned_classes else None)

    months = Month.objects.all().order_by("id")
    selected_month_id = request.GET.get("month_id") or request.POST.get("month_id")
    if selected_month_id and str(selected_month_id).isdigit():
        selected_month = Month.objects.filter(id=int(selected_month_id)).first()
    else:
        selected_month = months.first()

    academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
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
        return redirect(f"{reverse('teachers:attendance')}?class_id={selected_class.id}&month_id={selected_month.id}")

    student_rows = []
    if selected_class and selected_month:
        enrollments = (
            StudentClass.objects.filter(classs=selected_class, academice_year=academic_year)
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

    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/attendance.html", context)


@teacher_access_required
def teacher_assessment_view(request):
    """
    Monthly Assessment Entry for Teacher's Subjects (ثبت ارزیابی‌های ماهوار شاگردان).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    assigned_classes = get_teacher_assigned_classes(teacher)

    selected_class_id = request.GET.get("class_id") or request.POST.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        selected_class = assigned_classes[0] if assigned_classes else None

    assigned_subjects = get_teacher_assigned_subjects(teacher, selected_class)
    selected_subject_id = request.GET.get("subject_id") or request.POST.get("subject_id")
    if selected_subject_id and str(selected_subject_id).isdigit():
        selected_subject = Subject.objects.filter(id=int(selected_subject_id)).first()
    else:
        selected_subject = assigned_subjects[0] if assigned_subjects else None

    months = Month.objects.all().order_by("id")
    selected_month_id = request.GET.get("month_id") or request.POST.get("month_id")
    if selected_month_id and str(selected_month_id).isdigit():
        selected_month = Month.objects.filter(id=int(selected_month_id)).first()
    else:
        selected_month = months.first()

    academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
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
        return redirect(f"{reverse('teachers:assessment')}?class_id={selected_class.id}&subject_id={selected_subject.id}&month_id={selected_month.id}")

    student_rows = []
    if selected_class and selected_subject and selected_month:
        enrollments = (
            StudentClass.objects.filter(classs=selected_class, academice_year=academic_year)
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

    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/assessment.html", context)


@teacher_access_required
def teacher_shaqqa_view(request):
    """
    Digital Shaqqa & Exam Marks Entry for Teacher's Subjects
    (ورود نمرات شقه امتحانات چهارونیم ماهه و سالانه مطابق طرزالعمل معارف).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    assigned_classes = get_teacher_assigned_classes(teacher)

    selected_class_id = request.GET.get("class_id") or request.POST.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        selected_class = assigned_classes[0] if assigned_classes else None

    assigned_subjects = get_teacher_assigned_subjects(teacher, selected_class)
    selected_subject_id = request.GET.get("subject_id") or request.POST.get("subject_id")
    if selected_subject_id and str(selected_subject_id).isdigit():
        selected_subject = Subject.objects.filter(id=int(selected_subject_id)).first()
    else:
        selected_subject = assigned_subjects[0] if assigned_subjects else None

    academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()

    if request.method == "POST" and selected_class and selected_subject:
        saved_count = save_teacher_shaqqa_matrix(
            teacher, selected_class, selected_subject, academic_year, request.POST
        )
        messages.success(
            request,
            f"شقه نمرات امتحان مضمون «{selected_subject.name}» برای صنف {selected_class.alpha_grade} شعبه {selected_class.section} با موفقیت ({saved_count} شاگرد) در سیستم امتحانات معارف ذخیره گردید."
        )
        return redirect(f"{reverse('teachers:shaqqa')}?class_id={selected_class.id}&subject_id={selected_subject.id}")

    matrix_data = None
    if selected_class and selected_subject:
        matrix_data = get_teacher_shaqqa_matrix(teacher, selected_class, selected_subject, academic_year)

    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/shaqqa.html", context)


@teacher_access_required
def teacher_my_timetable_view(request):
    """
    Teacher's Personal Weekly Timetable (تقسیم اوقات تدریس هفتگی استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
    matrix_data = get_teacher_timetable_matrix(teacher.id, academic_year.id if academic_year else None)

    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/my_timetable.html", context)


@teacher_access_required
def teacher_class_timetable_view(request):
    """
    Weekly Timetable of Teacher's Guided Class (تقسیم اوقات صنف تحت نگران استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    assigned_classes = get_teacher_assigned_classes(teacher)
    guidance_class = Classes.objects.filter(guidence=teacher).first()

    selected_class_id = request.GET.get("class_id")
    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        selected_class = guidance_class or (assigned_classes[0] if assigned_classes else None)

    academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()

    matrix_data = None
    if selected_class:
        matrix_data = get_class_timetable_matrix(selected_class.id, academic_year.id if academic_year else None)

    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/class_timetable.html", context)


@teacher_access_required
def teacher_students_view(request):
    """
    Student Roster for Teacher's Classes (لیست شاگردان صنوف استاد).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    assigned_classes = get_teacher_assigned_classes(teacher)
    selected_class_id = request.GET.get("class_id")
    search_query = request.GET.get("search", "").strip()

    if selected_class_id and str(selected_class_id).isdigit():
        selected_class = Classes.objects.filter(id=int(selected_class_id)).first()
    else:
        selected_class = None

    academic_year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()

    enrollments_qs = StudentClass.objects.filter(academice_year=academic_year).select_related("student", "classs")

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

    students = [sc.student for sc in enrollments_qs.order_by("classs__grade", "classs__section", "student__name")]
    all_teachers = Teacher.objects.filter(status_id=1).order_by("name") if request.user.is_staff else []

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
    return render(request, "teachers/students.html", context)


@teacher_access_required
def teacher_profile_view(request):
    """
    Teacher Profile View (مشخصات، سوابق و پرونده استادی).
    """
    teacher = get_current_teacher_profile(request)
    if not teacher:
        return redirect(reverse("teachers:dashboard"))

    years = AcademiceYear.objects.all().order_by("-year")
    academic_year = AcademiceYear.objects.filter(year=1403).first() or years.first()
    kpis = get_teacher_kpis(teacher, academic_year)
    assigned_classes = get_teacher_assigned_classes(teacher)
    assigned_subjects = get_teacher_assigned_subjects(teacher)

    context = {
        "teacher": teacher,
        "kpis": kpis,
        "assigned_classes": assigned_classes,
        "assigned_subjects": assigned_subjects,
        "academic_year": academic_year,
        "today_str": get_current_jalali_date_str(),
    }
    return render(request, "teachers/profile.html", context)
