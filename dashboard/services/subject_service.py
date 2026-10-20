"""
Subject & Afghan Curriculum Management Service
(مدیریت مضامین و نصاب تعلیمی مکاتب معارف افغانستان)
Strictly adheres to Afghanistan Ministry of Education (طرزالعمل و لوایح وزارت معارف):
- Categorization into Islamic studies, languages, natural sciences, mathematics, social studies, IT & sports.
- Support for Primary (ابتدائیه ۱-۶), Middle (متوسطه ۷-۹), and High School (لیسه ۱۰-۱۲).
- Automated curriculum standard application, teacher-subject matrix, and safety validations.
"""

from typing import Dict, Any, List, Tuple, Optional
from django.db.models import Count, Avg, Q, Sum
from dashboard.models import (
    Subject,
    Classes,
    Teacher,
    TeacherSubject,
    TimeTable,
    ExamMark,
    Assessment,
    StudentClass,
    AcademiceYear,
)


# Standard Afghan Ministry of Education Curriculum Definitions
MOE_CURRICULUM_STANDARDS = {
    "ابتدائیه": [
        "قرآن کریم و تجوید",
        "تعلیمات دینی و تفسیر",
        "تهذیب و اخلاق اسلامی",
        "ادبیات و قرائت دری",
        "زبان و ادبیات پشتو",
        "ریاضیات دوره ابتدائیه",
        "ساینس و محیط زیست",
        "حسن خط و رسم",
        "تعلیم و تربیه بدنی",
    ],
    "متوسطه": [
        "قرآن کریم و تجوید",
        "عقاید و فقه",
        "تعلیمات دینی و تفسیر",
        "ادبیات و قرائت دری",
        "زبان و ادبیات پشتو",
        "لسان انگلیسی",
        "ریاضیات عالی",
        "فزیک",
        "کیمیا",
        "بیولوژی",
        "تاریخ معاصر افغانستان",
        "جغرافیه عمومی",
        "کمپیوتر و فناوری معلومات",
        "حسن خط و رسم",
        "تعلیم و تربیه بدنی",
    ],
    "لیسه": [
        "قرآن کریم و تجوید",
        "تعلیمات دینی و تفسیر",
        "ادبیات و قرائت دری",
        "زبان و ادبیات پشتو",
        "لسان انگلیسی",
        "ریاضیات عالی",
        "هندسه و مثلثات",
        "فزیک",
        "کیمیا",
        "بیولوژی",
        "تاریخ معاصر افغانستان",
        "جغرافیه عمومی",
        "کمپیوتر و فناوری معلومات",
        "تعلیم و تربیه بدنی",
    ],
}


def get_afghan_curriculum_standards() -> Dict[str, List[str]]:
    """Return the Afghan MoE curriculum standard subjects by educational level."""
    return MOE_CURRICULUM_STANDARDS


def get_class_educational_stage(class_obj: Classes) -> str:
    """Determine the educational stage based on the grade number."""
    grade = class_obj.grade or 1
    if grade <= 6:
        return "ابتدائیه"
    elif 7 <= grade <= 9:
        return "متوسطه"
    else:
        return "لیسه"


def apply_afghan_curriculum_to_class(class_obj: Classes, stage: Optional[str] = None) -> Dict[str, Any]:
    """
    Applies the official Ministry of Education standard subject list to a class.
    Assigns the appropriate curriculum subjects based on stage/grade.
    """
    if not stage:
        stage = get_class_educational_stage(class_obj)

    standard_names = MOE_CURRICULUM_STANDARDS.get(stage, MOE_CURRICULUM_STANDARDS["لیسه"])
    subjects_to_assign = []

    for name in standard_names:
        subj = Subject.objects.filter(name=name).first()
        if not subj:
            subj = Subject.objects.create(
                name=name,
                educational_level=stage,
                weekly_hours=3,
                passing_score=40.0,
                total_score=100.0,
                is_active=True,
            )
        subjects_to_assign.append(subj)

    class_obj.subjects.set(subjects_to_assign)

    return {
        "class": class_obj,
        "stage": stage,
        "assigned_count": len(subjects_to_assign),
        "subjects": subjects_to_assign,
    }


def get_subject_statistics() -> Dict[str, Any]:
    """Calculate overview KPIs across all curriculum subjects."""
    total_subjects = Subject.objects.count()
    active_subjects = Subject.objects.filter(is_active=True).count()
    inactive_subjects = total_subjects - active_subjects

    hours_agg = Subject.objects.filter(is_active=True).aggregate(total=Sum("weekly_hours"))
    total_weekly_hours = hours_agg["total"] or 0

    category_counts = (
        Subject.objects.values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    level_counts = (
        Subject.objects.values("educational_level")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    return {
        "total_subjects": total_subjects,
        "active_subjects": active_subjects,
        "inactive_subjects": inactive_subjects,
        "total_weekly_hours": total_weekly_hours,
        "category_counts": list(category_counts),
        "level_counts": list(level_counts),
        "total_classes": Classes.objects.count(),
    }


def get_subject_detail_metrics(subject: Subject) -> Dict[str, Any]:
    """Detailed profile data and academic metrics for a single subject."""
    assigned_classes = list(subject.classes.all().order_by("grade", "section"))
    
    # Teachers teaching this subject (from TeacherSubject and TimeTable)
    tt_teacher_ids = list(
        TimeTable.objects.filter(subject=subject)
        .values_list("teacher_id", flat=True)
        .distinct()
    )
    ts_teacher_ids = list(
        TeacherSubject.objects.filter(subject=subject)
        .values_list("teacher_id", flat=True)
        .distinct()
    )
    all_teacher_ids = set(tt_teacher_ids + ts_teacher_ids)
    teachers = list(Teacher.objects.filter(id__in=all_teacher_ids).order_by("name"))

    # Enrolled students across assigned classes
    total_students = StudentClass.objects.filter(classs__in=assigned_classes).values("student_id").distinct().count()

    # Exam performance statistics
    marks_qs = ExamMark.objects.filter(subject=subject)
    total_marks_records = marks_qs.count()
    
    if total_marks_records > 0:
        avg_midterm = marks_qs.aggregate(avg=Avg("midterm_marks"))["avg"] or 0
        avg_final = marks_qs.aggregate(avg=Avg("final_marks"))["avg"] or 0
        avg_total = round(float(avg_midterm) + float(avg_final), 1)
        passed_marks_count = sum(1 for m in marks_qs if m.is_passed)
        pass_rate = round((passed_marks_count / total_marks_records) * 100, 1)
    else:
        avg_total = 0.0
        pass_rate = 0.0

    timetable_slots_count = TimeTable.objects.filter(subject=subject).count()

    return {
        "subject": subject,
        "assigned_classes": assigned_classes,
        "classes_count": len(assigned_classes),
        "teachers": teachers,
        "teachers_count": len(teachers),
        "total_students": total_students,
        "total_marks_records": total_marks_records,
        "avg_total_mark": avg_total,
        "pass_rate": pass_rate,
        "timetable_slots_count": timetable_slots_count,
    }


def validate_subject_deletion(subject: Subject) -> Dict[str, Any]:
    """
    Validate if a subject can be safely deleted or must be deactivated instead.
    Maintains academic record integrity.
    """
    exam_marks_count = ExamMark.objects.filter(subject=subject).count()
    timetable_count = TimeTable.objects.filter(subject=subject).count()
    assessment_count = Assessment.objects.filter(subject=subject).count()
    teachersubject_count = TeacherSubject.objects.filter(subject=subject).count()

    has_dependencies = (
        exam_marks_count > 0 or
        timetable_count > 0 or
        assessment_count > 0 or
        teachersubject_count > 0
    )

    can_delete = not has_dependencies
    reason = ""

    if has_dependencies:
        dep_items = []
        if exam_marks_count > 0:
            dep_items.append(f"{exam_marks_count} نمره امتحان در شقه نمرات")
        if timetable_count > 0:
            dep_items.append(f"{timetable_count} ساعت درسی در تقسیم اوقات")
        if assessment_count > 0:
            dep_items.append(f"{assessment_count} نمره ارزیابی ماهوار")
        if teachersubject_count > 0:
            dep_items.append(f"{teachersubject_count} سابقه تخصیص استاد")

        reason = (
            f"مضمون «{subject.name}» به دلیل داشتن سوابق فعال تعلیمی ("
            + "، ".join(dep_items)
            + ") قابل حذف قطعی نیست. برای خارج کردن آن از نصاب تعلیمی جاری، لطفاً وضعیت آن را به «غیرفعال» تغییر دهید."
        )

    return {
        "can_delete": can_delete,
        "reason": reason,
        "counts": {
            "exam_marks": exam_marks_count,
            "timetable": timetable_count,
            "assessment": assessment_count,
            "teachersubject": teachersubject_count,
        },
    }
