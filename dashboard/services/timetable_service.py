"""
Timetable & Schedule Service for School Management System
Strictly following Afghanistan Ministry of Education (طرزالعمل تقسیم اوقات مکاتب معارف افغانستان):
- 6-Day School Week (Saturday to Thursday, Friday is official holiday)
- 6 Teaching Periods per day (ساعت اول تا ساعت ششم به همراه زنگ تفریح بین ساعت سوم و چهارم)
- Conflict detection (Double-booking prevention for teachers and classes)
"""

from typing import Dict, Any, List, Tuple, Optional
from dashboard.models import TimeTable, Classes, Teacher, Subject, AcademiceYear

DAYS = [
    {"num": 1, "name": "شنبه", "short": "ش"},
    {"num": 2, "name": "یک‌شنبه", "short": "ی"},
    {"num": 3, "name": "دوشنبه", "short": "د"},
    {"num": 4, "name": "سه‌شنبه", "short": "س"},
    {"num": 5, "name": "چهارشنبه", "short": "چ"},
    {"num": 6, "name": "پنج‌شنبه", "short": "پ"},
]

PERIODS = [
    {"num": 1, "name": "ساعت اول", "time": "۰۸:۰۰ - ۰۸:۴۵"},
    {"num": 2, "name": "ساعت دوم", "time": "۰۸:۴۵ - ۰۹:۳۰"},
    {"num": 3, "name": "ساعت سوم", "time": "۰۹:۳۰ - ۱۰:۱۵"},
    {"num": 4, "name": "ساعت چهارم", "time": "۱۰:۳۵ - ۱۱:۲۰"},
    {"num": 5, "name": "ساعت پنجم", "time": "۱۱:۲۰ - ۱۲:۰۵"},
    {"num": 6, "name": "ساعت ششم", "time": "۱۲:۰۵ - ۱۲:۵۰"},
]

RECESS_INFO = {
    "title": "زنگ تفریح و استراحت",
    "time": "۱۰:۱۵ - ۱۰:۳۵",
    "duration": "۲۰ دقیقه",
    "after_period": 3,
}


def get_class_timetable_matrix(class_id: int, academic_year_id: int) -> Dict[str, Any]:
    """
    Build 6x6 weekly schedule grid for a specific class.
    """
    slots = list(
        TimeTable.objects.filter(classs_id=class_id, academic_year_id=academic_year_id)
        .select_related("teacher", "subject", "classs", "academic_year")
    )

    slot_map = {(s.day_of_week, s.period): s for s in slots}

    weekly_grid = []
    for day in DAYS:
        day_slots = []
        for period in PERIODS:
            slot = slot_map.get((day["num"], period["num"]))
            day_slots.append({
                "period": period,
                "slot": slot,
                "is_empty": slot is None,
            })
        weekly_grid.append({
            "day": day,
            "slots": day_slots,
        })

    # Stats and breakdowns
    subject_counts: Dict[str, int] = {}
    teacher_counts: Dict[str, int] = {}
    for s in slots:
        sub_name = s.subject.name
        subject_counts[sub_name] = subject_counts.get(sub_name, 0) + 1
        t_name = f"{s.teacher.name} {s.teacher.last_name or ''}".strip()
        teacher_counts[t_name] = teacher_counts.get(t_name, 0) + 1

    total_capacity = 36  # 6 days * 6 periods
    assigned_count = len(slots)
    completion_rate = round((assigned_count / total_capacity) * 100, 1) if total_capacity > 0 else 0

    return {
        "weekly_grid": weekly_grid,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "total_assigned": assigned_count,
        "empty_slots_count": total_capacity - assigned_count,
        "completion_rate": completion_rate,
        "subject_counts": subject_counts,
        "teacher_counts": teacher_counts,
        "unique_teachers_count": len(teacher_counts),
        "unique_subjects_count": len(subject_counts),
    }


def get_teacher_timetable_matrix(teacher_id: int, academic_year_id: int) -> Dict[str, Any]:
    """
    Build 6x6 weekly schedule grid for a specific teacher.
    """
    slots = list(
        TimeTable.objects.filter(teacher_id=teacher_id, academic_year_id=academic_year_id)
        .select_related("classs", "subject", "teacher", "academic_year")
    )

    slot_map = {(s.day_of_week, s.period): s for s in slots}

    weekly_grid = []
    for day in DAYS:
        day_slots = []
        for period in PERIODS:
            slot = slot_map.get((day["num"], period["num"]))
            day_slots.append({
                "period": period,
                "slot": slot,
                "is_empty": slot is None,
            })
        weekly_grid.append({
            "day": day,
            "slots": day_slots,
        })

    class_counts: Dict[str, int] = {}
    subject_counts: Dict[str, int] = {}
    for s in slots:
        c_name = f"{s.classs.alpha_grade} - {s.classs.section}"
        class_counts[c_name] = class_counts.get(c_name, 0) + 1
        sub_name = s.subject.name
        subject_counts[sub_name] = subject_counts.get(sub_name, 0) + 1

    total_periods = len(slots)
    free_hours = 36 - total_periods

    return {
        "weekly_grid": weekly_grid,
        "days": DAYS,
        "periods": PERIODS,
        "recess_info": RECESS_INFO,
        "total_teaching_hours": total_periods,
        "free_hours": free_hours,
        "class_counts": class_counts,
        "subject_counts": subject_counts,
        "distinct_classes_count": len(class_counts),
        "distinct_subjects_count": len(subject_counts),
    }


def validate_timetable_slot(
    class_id: int,
    teacher_id: int,
    day_of_week: int,
    period: int,
    academic_year_id: int,
    exclude_slot_id: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that neither the teacher nor the class has a scheduling conflict.
    """
    # 1. Check teacher double booking
    teacher_qs = TimeTable.objects.filter(
        teacher_id=teacher_id,
        day_of_week=day_of_week,
        period=period,
        academic_year_id=academic_year_id,
    ).select_related("classs", "subject", "teacher")

    if exclude_slot_id:
        teacher_qs = teacher_qs.exclude(id=exclude_slot_id)

    t_conflict = teacher_qs.first()
    if t_conflict:
        t_name = f"{t_conflict.teacher.name} {t_conflict.teacher.last_name or ''}".strip()
        c_name = f"{t_conflict.classs.alpha_grade} - {t_conflict.classs.section}"
        return (
            False,
            f"تداخل زمانی استاد: استاد «{t_name}» در روز {t_conflict.day_name} {t_conflict.period_name} "
            f"در صنف «{c_name}» مشغول تدریس مضمون «{t_conflict.subject.name}» می‌باشد و نمی‌تواند همزمان در دو صنف حاضر باشد."
        )

    # 2. Check class double booking
    class_qs = TimeTable.objects.filter(
        classs_id=class_id,
        day_of_week=day_of_week,
        period=period,
        academic_year_id=academic_year_id,
    ).select_related("classs", "subject", "teacher")

    if exclude_slot_id:
        class_qs = class_qs.exclude(id=exclude_slot_id)

    c_conflict = class_qs.first()
    if c_conflict:
        t_name = f"{c_conflict.teacher.name} {c_conflict.teacher.last_name or ''}".strip()
        c_name = f"{c_conflict.classs.alpha_grade} - {c_conflict.classs.section}"
        return (
            False,
            f"تداخل زمانی صنف: صنف «{c_name}» در روز {c_conflict.day_name} {c_conflict.period_name} "
            f"قبلاً برای مضمون «{c_conflict.subject.name}» با استاد «{t_name}» ثبت گردیده است."
        )

    return (True, None)


def get_master_timetable_matrix(academic_year_id: int, day_of_week: int) -> Dict[str, Any]:
    """
    Build master school matrix for all classes for a specific day of the week.
    """
    classes = list(Classes.objects.all().order_by("grade", "section"))
    slots = list(
        TimeTable.objects.filter(academic_year_id=academic_year_id, day_of_week=day_of_week)
        .select_related("classs", "teacher", "subject")
    )

    slot_map = {(s.classs_id, s.period): s for s in slots}

    class_rows = []
    for cls in classes:
        p_slots = []
        for period in PERIODS:
            slot = slot_map.get((cls.id, period["num"]))
            p_slots.append({
                "period": period,
                "slot": slot,
            })
        class_rows.append({
            "class": cls,
            "slots": p_slots,
        })

    day_obj = next((d for d in DAYS if d["num"] == day_of_week), DAYS[0])

    return {
        "day": day_obj,
        "days": DAYS,
        "periods": PERIODS,
        "class_rows": class_rows,
        "total_classes": len(classes),
        "total_slots_day": len(slots),
    }
