"""
Teacher Portal & Academic Workflow Service for Afghan School System
(سرویس پورتال اساتید، مدیریت حاضری، ارزیابی، شقه نمرات و تقسیم اوقات تدریس)
Strictly adheres to Afghanistan Ministry of Education (طرزالعمل وزارت معارف):
- Roster management for classes taught and guided.
- Guidance teacher attendance authority.
- Subject-based monthly assessments.
- Midterm (40) and Annual (60) exam marks entry with automatic Afghan MoE results logic.
- Weekly teaching timetable matrix and daily schedule.
"""

from typing import Dict, Any, List, Optional, Set
import jdatetime
import datetime
from django.db.models import Q, Count, Sum, Avg
from dashboard.models import (
    Teacher,
    Classes,
    Subject,
    Student,
    StudentClass,
    Attendance,
    Assessment,
    ExamMark,
    TimeTable,
    Month,
    AcademiceYear,
    TeacherSubject,
)
from dashboard.services.timetable_service import DAYS, PERIODS, RECESS_INFO


def get_current_teacher_profile(request) -> Optional[Teacher]:
    """
    Resolve the active Teacher instance for the current request:
    1. If request.user has a linked teacher_profile, returns that teacher.
    2. If request.user is staff: allows selecting via ?teacher_id=... or session.
    3. Fallback for staff: first active teacher in database.
    """
    if not request.user.is_authenticated:
        return None

    if hasattr(request.user, "teacher_profile") and request.user.teacher_profile:
        return request.user.teacher_profile

    if request.user.is_staff:
        teacher_id = request.GET.get("teacher_id") or request.session.get("active_teacher_id")
        if teacher_id and str(teacher_id).isdigit():
            t = Teacher.objects.filter(id=int(teacher_id)).first()
            if t:
                request.session["active_teacher_id"] = t.id
                return t

        # Default fallback: guidance teacher of Class 10-A or first active teacher
        cls_10 = Classes.objects.filter(grade=10, section="الف", guidence__isnull=False).first()
        if cls_10 and cls_10.guidence:
            request.session["active_teacher_id"] = cls_10.guidence.id
            return cls_10.guidence

        first_t = Teacher.objects.filter(status_id=1).first() or Teacher.objects.first()
        if first_t:
            request.session["active_teacher_id"] = first_t.id
            return first_t

    return None


def get_teacher_assigned_classes(teacher: Teacher) -> List[Classes]:
    """
    Retrieve all classes associated with this teacher:
    - Classes where this teacher is guidance teacher (نگران صنف)
    - Classes where this teacher teaches in TimeTable
    - Classes in TeacherSubject
    """
    guidance_class_ids = set(Classes.objects.filter(guidence=teacher).values_list("id", flat=True))
    tt_class_ids = set(TimeTable.objects.filter(teacher=teacher).values_list("classs_id", flat=True))
    ts_class_ids = set(TeacherSubject.objects.filter(teacher=teacher).values_list("classs_id", flat=True))

    all_class_ids = guidance_class_ids | tt_class_ids | ts_class_ids

    if not all_class_ids:
        # Fallback if no specific assignment: return classes where teacher is assigned or first classes
        all_class_ids = set(Classes.objects.values_list("id", flat=True)[:3])

    return list(Classes.objects.filter(id__in=all_class_ids).order_by("grade", "section"))


def get_teacher_assigned_subjects(teacher: Teacher, class_obj: Optional[Classes] = None) -> List[Subject]:
    """
    Retrieve distinct subjects taught by this teacher (optionally filtered for a specific class).
    """
    tt_qs = TimeTable.objects.filter(teacher=teacher)
    ts_qs = TeacherSubject.objects.filter(teacher=teacher)

    if class_obj:
        tt_qs = tt_qs.filter(classs=class_obj)
        ts_qs = ts_qs.filter(classs=class_obj)

    tt_subject_ids = set(tt_qs.values_list("subject_id", flat=True))
    ts_subject_ids = set(ts_qs.values_list("subject_id", flat=True))
    all_subject_ids = tt_subject_ids | ts_subject_ids

    # If teacher is guidance for this class, also allow class curriculum subjects
    if class_obj and class_obj.guidence == teacher:
        all_subject_ids |= set(class_obj.subjects.values_list("id", flat=True))

    if not all_subject_ids:
        if class_obj and class_obj.subjects.exists():
            return list(class_obj.subjects.all().order_by("name"))
        return list(Subject.objects.filter(is_active=True).order_by("name")[:5])

    return list(Subject.objects.filter(id__in=all_subject_ids).order_by("name"))


def get_current_jalali_day_info() -> Dict[str, Any]:
    """
    Determine today's day number in the Afghan school week:
    Saturday (شنبه) = 1
    Sunday (یک‌شنبه) = 2
    Monday (دوشنبه) = 3
    Tuesday (سه‌شنبه) = 4
    Wednesday (چهارشنبه) = 5
    Thursday (پنج‌شنبه) = 6
    Friday (جمعه) = 7 (Holiday)
    """
    try:
        j_today = jdatetime.date.today()
        # jdatetime weekday(): Monday is 0, Sunday is 6, Saturday is 5
        # Let's map directly:
        day_names = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
        day_mapping = {
            5: (1, "شنبه"),
            6: (2, "یک‌شنبه"),
            0: (3, "دوشنبه"),
            1: (4, "سه‌شنبه"),
            2: (5, "چهارشنبه"),
            3: (6, "پنج‌شنبه"),
            4: (7, "جمعه"),
        }
        weekday_idx = j_today.weekday()
        day_num, day_name = day_mapping.get(weekday_idx, (1, "شنبه"))
        month_names = [
            "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
            "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"
        ]
        formatted_date = f"{day_name}، {j_today.day} {month_names[j_today.month - 1]} {j_today.year}"
        return {
            "day_num": day_num,
            "day_name": day_name,
            "is_friday": day_num == 7,
            "formatted_date": formatted_date,
            "jalali_date": j_today,
        }
    except Exception:
        return {
            "day_num": 1,
            "day_name": "شنبه",
            "is_friday": False,
            "formatted_date": "شنبه، ۱ حمل ۱۴۰۳",
            "jalali_date": None,
        }


def get_teacher_today_schedule(teacher: Teacher, academic_year_id: int) -> Dict[str, Any]:
    """
    Build today's 6-period teaching schedule for this teacher.
    """
    day_info = get_current_jalali_day_info()

    if day_info["is_friday"]:
        return {
            "is_holiday": True,
            "day_info": day_info,
            "message": "امروز جمعه و رخصتی عمومی تعلیمی مکاتب معارف می‌باشد.",
            "slots": [],
            "teaching_periods_count": 0,
        }

    # Query timetable for today
    slots_qs = (
        TimeTable.objects.filter(
            teacher=teacher,
            academic_year_id=academic_year_id,
            day_of_week=day_info["day_num"]
        )
        .select_related("classs", "subject")
        .order_by("period")
    )

    slot_map = {s.period: s for s in slots_qs}

    today_periods = []
    teaching_count = 0
    for p in PERIODS:
        slot = slot_map.get(p["num"])
        is_teaching = slot is not None
        if is_teaching:
            teaching_count += 1
        today_periods.append({
            "period": p,
            "slot": slot,
            "is_teaching": is_teaching,
        })

    return {
        "is_holiday": False,
        "day_info": day_info,
        "periods": today_periods,
        "teaching_periods_count": teaching_count,
        "recess_info": RECESS_INFO,
    }


def get_teacher_kpis(teacher: Teacher, academic_year: AcademiceYear) -> Dict[str, Any]:
    """
    Calculate summary KPIs for the teacher dashboard overview.
    """
    assigned_classes = get_teacher_assigned_classes(teacher)
    assigned_subjects = get_teacher_assigned_subjects(teacher)

    weekly_hours_count = TimeTable.objects.filter(
        teacher=teacher, academic_year=academic_year
    ).count()

    total_students = StudentClass.objects.filter(
        classs__in=assigned_classes, academice_year=academic_year
    ).values("student_id").distinct().count()

    guidance_class = Classes.objects.filter(guidence=teacher).first()
    guidance_students_count = 0
    if guidance_class:
        guidance_students_count = StudentClass.objects.filter(
            classs=guidance_class, academice_year=academic_year
        ).count()

    # Assessments recorded by this teacher
    assessments_count = Assessment.objects.filter(
        teacher=teacher, academice_year=academic_year
    ).count()

    # Exam marks recorded for teacher's subjects and classes
    marks_count = ExamMark.objects.filter(
        classs__in=assigned_classes,
        subject__in=assigned_subjects,
        academice_year=academic_year
    ).count()

    return {
        "total_classes": len(assigned_classes),
        "total_subjects": len(assigned_subjects),
        "weekly_hours_count": weekly_hours_count,
        "total_students": total_students,
        "guidance_class": guidance_class,
        "guidance_students_count": guidance_students_count,
        "assessments_count": assessments_count,
        "marks_count": marks_count,
    }


def get_teacher_shaqqa_matrix(
    teacher: Teacher,
    class_obj: Classes,
    subject_obj: Subject,
    academic_year: AcademiceYear
) -> Dict[str, Any]:
    """
    Load student roster and exam marks for this teacher, class, and subject.
    Strictly calculates MoE rules (Midterm 40, Final 60).
    """
    enrollments = (
        StudentClass.objects.filter(classs=class_obj, academice_year=academic_year)
        .select_related("student")
        .order_by("student__name")
    )

    marks_qs = ExamMark.objects.filter(
        classs=class_obj,
        subject=subject_obj,
        academice_year=academic_year
    ).select_related("student")

    marks_map = {m.student_id: m for m in marks_qs}

    student_rows = []
    for sc in enrollments:
        std = sc.student
        mark_rec = marks_map.get(std.id)
        midterm = float(mark_rec.midterm_marks or 0) if mark_rec else 0.0
        final = float(mark_rec.final_marks or 0) if mark_rec else 0.0
        cond = float(mark_rec.conditional_marks) if mark_rec and mark_rec.conditional_marks is not None else None
        total = round(midterm + final, 1)
        is_pass = (total >= 40.0 and final >= 24.0) if mark_rec else False
        is_mhr = mark_rec.is_mahroom if mark_rec else False
        is_mzr = mark_rec.is_mazrati if mark_rec else False
        notes = mark_rec.notes or "" if mark_rec else ""

        if is_mhr:
            status_lbl = "محروم"
            badge_cls = "badge-danger"
        elif is_mzr:
            status_lbl = "معذرتی"
            badge_cls = "badge-warning"
        elif cond is not None:
            status_lbl = "کامیاب (مشروطی)" if cond >= 40.0 else "ناکام"
            badge_cls = "badge-success" if cond >= 40.0 else "badge-danger"
        elif mark_rec and total > 0:
            status_lbl = "کامیاب" if is_pass else "ناکام"
            badge_cls = "badge-success" if is_pass else "badge-danger"
        else:
            status_lbl = "ثبت‌نشده"
            badge_cls = "badge-secondary"

        student_rows.append({
            "student": std,
            "midterm": midterm,
            "final": final,
            "conditional": cond,
            "total": total,
            "is_passed": is_pass,
            "is_mahroom": is_mhr,
            "is_mazrati": is_mzr,
            "status_label": status_lbl,
            "badge_class": badge_cls,
            "notes": notes,
            "has_record": mark_rec is not None,
        })

    total_count = len(student_rows)
    passed_count = sum(1 for r in student_rows if r["is_passed"])
    failed_count = sum(1 for r in student_rows if r["status_label"] == "ناکام")
    avg_score = round(sum(r["total"] for r in student_rows) / total_count, 1) if total_count > 0 else 0.0

    return {
        "class": class_obj,
        "subject": subject_obj,
        "academic_year": academic_year,
        "student_rows": student_rows,
        "total_count": total_count,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "avg_score": avg_score,
    }


def save_teacher_shaqqa_matrix(
    teacher: Teacher,
    class_obj: Classes,
    subject_obj: Subject,
    academic_year: AcademiceYear,
    post_data: Any
) -> int:
    """
    Save bulk student marks entered by the teacher.
    Validates midterm <= 40, final <= 60.
    """
    enrollments = StudentClass.objects.filter(
        classs=class_obj, academice_year=academic_year
    ).select_related("student")

    saved_count = 0
    for sc in enrollments:
        std = sc.student
        m_key = f"midterm_{std.id}"
        f_key = f"final_{std.id}"
        c_key = f"cond_{std.id}"
        mhr_key = f"mahroom_{std.id}"
        mzr_key = f"mazrati_{std.id}"
        notes_key = f"notes_{std.id}"

        if m_key in post_data or f_key in post_data:
            raw_mid = post_data.get(m_key, "")
            raw_fin = post_data.get(f_key, "")
            raw_cond = post_data.get(c_key, "")
            is_mhr = post_data.get(mhr_key) == "1"
            is_mzr = post_data.get(mzr_key) == "1"
            notes = post_data.get(notes_key, "").strip()

            try:
                mid_val = min(40.0, max(0.0, float(raw_mid))) if raw_mid != "" else 0.0
            except (ValueError, TypeError):
                mid_val = 0.0

            try:
                fin_val = min(60.0, max(0.0, float(raw_fin))) if raw_fin != "" else 0.0
            except (ValueError, TypeError):
                fin_val = 0.0

            cond_val = None
            if raw_cond != "":
                try:
                    cond_val = min(100.0, max(0.0, float(raw_cond)))
                except (ValueError, TypeError):
                    cond_val = None

            ExamMark.objects.update_or_create(
                student=std,
                classs=class_obj,
                subject=subject_obj,
                academice_year=academic_year,
                defaults={
                    "midterm_marks": mid_val,
                    "final_marks": fin_val,
                    "conditional_marks": cond_val,
                    "is_mahroom": is_mhr,
                    "is_mazrati": is_mzr,
                    "notes": notes,
                }
            )
            saved_count += 1

    return saved_count
