"""
Exam and Grading Service strictly implementing:
طرزالعمل و لوایح امتحانات وزارت معارف افغانستان (Afghanistan Ministry of Education)
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from dashboard.models import (
    Student,
    Classes,
    Subject,
    AcademiceYear,
    StudentClass,
    TeacherSubject,
    ExamMark,
    ExamAttendance,
)


def get_class_subjects(class_obj: Classes) -> List[Subject]:
    """
    Retrieve curriculum subjects assigned to a class.
    Fallback priority:
    1. Direct class.subjects ManyToMany relation.
    2. TeacherSubject records assigned to this class.
    3. Default subjects in the system.
    """
    subjects = list(class_obj.subjects.all().order_by("id"))
    if not subjects:
        ts_subject_ids = TeacherSubject.objects.filter(classs=class_obj).values_list("subject_id", flat=True).distinct()
        if ts_subject_ids:
            subjects = list(Subject.objects.filter(id__in=ts_subject_ids).order_by("id"))
    if not subjects:
        subjects = list(Subject.objects.all().order_by("id"))
    return subjects


def calculate_grade(percentage: float) -> Dict[str, str]:
    """
    Grade calculation based on Afghanistan MoE rules:
    - 90% - 100%: الف (عالی)
    - 80% - 89.99%: ب (خوب جداً)
    - 70% - 79.99%: ج (خوب)
    - 55% - 69.99%: د (متوسط)
    - 40% - 54.99%: هـ (قابل قبول)
    - Below 40%: و (ضعیف / ناکام)
    """
    p = round(percentage, 2)
    if p >= 90.0:
        return {"code": "الف", "title": "عالی", "full": "الف (عالی)", "color": "#059669"}
    elif p >= 80.0:
        return {"code": "ب", "title": "خوب جداً", "full": "ب (خوب جداً)", "color": "#2563eb"}
    elif p >= 70.0:
        return {"code": "ج", "title": "خوب", "full": "ج (خوب)", "color": "#0284c7"}
    elif p >= 55.0:
        return {"code": "د", "title": "متوسط", "full": "د (متوسط)", "color": "#d97706"}
    elif p >= 40.0:
        return {"code": "هـ", "title": "قابل قبول", "full": "هـ (قابل قبول)", "color": "#e11d48"}
    else:
        return {"code": "و", "title": "ضعیف / ناکام", "full": "و (ضعیف / ناکام)", "color": "#dc2626"}


def format_rank_afghan(rank_number: int) -> str:
    """
    Converts numeric rank to traditional Afghan honor title:
    1 -> اول نمره
    2 -> دوم نمره
    3 -> سوم نمره
    4+ -> مقام ۴، مقام ۵ ...
    """
    if rank_number == 1:
        return "اول نمره"
    elif rank_number == 2:
        return "دوم نمره"
    elif rank_number == 3:
        return "سوم نمره"
    elif rank_number > 3:
        return f"مقام {rank_number}"
    return "-"


def calculate_student_result(
    student: Student,
    class_obj: Classes,
    academic_year: AcademiceYear,
    subjects: Optional[List[Subject]] = None,
    exam_marks_map: Optional[Dict[int, ExamMark]] = None,
    attendance: Optional[ExamAttendance] = None,
) -> Dict[str, Any]:
    """
    Calculate annual result for a single student based on MoE rules.
    """
    if subjects is None:
        subjects = get_class_subjects(class_obj)

    if exam_marks_map is None:
        records = ExamMark.objects.filter(
            student=student,
            classs=class_obj,
            academice_year=academic_year,
            subject__in=subjects,
        )
        exam_marks_map = {rec.subject_id: rec for rec in records}

    if attendance is None:
        attendance = ExamAttendance.objects.filter(
            student=student, classs=class_obj, academice_year=academic_year
        ).first()

    subject_rows = []
    grand_total = 0.0
    failed_subjects = []
    passed_subjects = []
    is_any_mahroom = False
    is_any_mazrati = False

    for subj in subjects:
        mark_rec = exam_marks_map.get(subj.id)
        if mark_rec:
            midterm = float(mark_rec.midterm_marks or 0)
            final = float(mark_rec.final_marks or 0)
            cond = float(mark_rec.conditional_marks) if mark_rec.conditional_marks is not None else None
            tot = mark_rec.total_marks
            eff = mark_rec.effective_marks
            is_pass = mark_rec.is_passed
            is_mhr = mark_rec.is_mahroom
            is_mzr = mark_rec.is_mazrati
            notes = mark_rec.notes or ""
            status_lbl = mark_rec.status_label
        else:
            midterm = 0.0
            final = 0.0
            cond = None
            tot = 0.0
            eff = 0.0
            is_pass = False
            is_mhr = False
            is_mzr = False
            notes = "ثبت‌نشده"
            status_lbl = "ثبت‌نشده"

        if is_mhr:
            is_any_mahroom = True
        if is_mzr:
            is_any_mazrati = True

        if is_pass:
            passed_subjects.append(subj)
        else:
            failed_subjects.append(subj)

        grand_total += eff
        subject_rows.append({
            "subject": subj,
            "midterm": midterm,
            "final": final,
            "conditional": cond,
            "total": tot,
            "effective": eff,
            "is_passed": is_pass,
            "is_mahroom": is_mhr,
            "is_mazrati": is_mzr,
            "status_label": status_lbl,
            "notes": notes,
            "mark_id": mark_rec.id if mark_rec else None,
        })

    subject_count = len(subjects)
    max_possible = subject_count * 100
    percentage = round((grand_total / max_possible * 100), 2) if max_possible > 0 else 0.0
    grade_info = calculate_grade(percentage)

    failed_count = len(failed_subjects)

    # Final Result Decision per Afghan MoE:
    # 1. محروم: Marked is_mahroom or attendance exceeds absence limit
    # 2. معذرتی: Marked is_mazrati
    # 3. کامیاب: 0 failed subjects (each total >= 40 and final >= 24)
    # 4. مشروط: 1, 2, or 3 failed subjects
    # 5. ناکام: 4 or more failed subjects
    if is_any_mahroom:
        result_status = "محروم"
        result_desc = "محروم از امتحان به دلیل غیبت بیش از حد مجاز یا محرومیت انضباطی"
        result_code = "mahroom"
        badge_class = "badge-danger"
    elif is_any_mazrati:
        result_status = "معذرتی"
        result_desc = "معذرتی با داشتن عذر موجه قانونی"
        result_code = "mazrati"
        badge_class = "badge-warning"
    elif failed_count == 0 and subject_count > 0:
        result_status = "کامیاب"
        result_desc = "ارتقاء به صنف بالاتر"
        result_code = "passed"
        badge_class = "badge-success"
    elif 1 <= failed_count <= 3:
        result_status = "مشروط"
        result_desc = f"مشروط در {failed_count} مضمون (چانس امتحان مشروطی)"
        result_code = "conditional"
        badge_class = "badge-warning"
    else:
        result_status = "ناکام"
        result_desc = "تکرار صنف (ناکام در چهار مضمون یا بیشتر)"
        result_code = "failed"
        badge_class = "badge-danger"

    return {
        "student": student,
        "class": class_obj,
        "academic_year": academic_year,
        "subjects": subjects,
        "subject_rows": subject_rows,
        "subject_marks_map": {r["subject"].id: r for r in subject_rows},
        "grand_total": round(grand_total, 1),
        "max_possible": max_possible,
        "percentage": percentage,
        "grade": grade_info["code"],
        "grade_title": grade_info["title"],
        "grade_full": grade_info["full"],
        "grade_color": grade_info["color"],
        "failed_count": failed_count,
        "passed_count": len(passed_subjects),
        "failed_subjects": failed_subjects,
        "result_status": result_status,
        "result_desc": result_desc,
        "result_code": result_code,
        "badge_class": badge_class,
        "is_passed": result_status == "کامیاب",
        "attendance": attendance,
        "rank": None,
        "rank_title": "-",
    }


def calculate_class_results(class_obj: Classes, academic_year: AcademiceYear) -> Dict[str, Any]:
    """
    Calculate master result sheet (جدول نتایج صنف) for all enrolled students in a class.
    Assigns class ranks (اول نمره، دوم نمره، سوم نمره) exclusively to passing students.
    """
    subjects = get_class_subjects(class_obj)
    enrollments = StudentClass.objects.filter(
        classs=class_obj, academice_year=academic_year
    ).select_related("student", "student__mother_language", "student__father_job").order_by("student__name")

    students = [e.student for e in enrollments]

    # Pre-fetch all marks for this class and year
    all_marks = ExamMark.objects.filter(
        classs=class_obj,
        academice_year=academic_year,
        subject__in=subjects,
    ).select_related("subject", "student")

    student_marks_lookup: Dict[int, Dict[int, ExamMark]] = {}
    for mark in all_marks:
        if mark.student_id not in student_marks_lookup:
            student_marks_lookup[mark.student_id] = {}
        student_marks_lookup[mark.student_id][mark.subject_id] = mark

    # Pre-fetch attendance
    all_attendance = ExamAttendance.objects.filter(
        classs=class_obj, academice_year=academic_year
    ).select_related("student")
    attendance_lookup = {att.student_id: att for att in all_attendance}

    results = []
    for std in students:
        marks_map = student_marks_lookup.get(std.id, {})
        att = attendance_lookup.get(std.id)
        res = calculate_student_result(
            student=std,
            class_obj=class_obj,
            academic_year=academic_year,
            subjects=subjects,
            exam_marks_map=marks_map,
            attendance=att,
        )
        results.append(res)

    # Ranking among passing students ("کامیاب")
    passing_results = [r for r in results if r["result_status"] == "کامیاب"]
    passing_results.sort(key=lambda r: (r["percentage"], r["grand_total"]), reverse=True)

    for idx, r in enumerate(passing_results, start=1):
        r["rank"] = idx
        r["rank_title"] = format_rank_afghan(idx)

    # Class aggregate statistics
    total_students = len(results)
    passed_count = sum(1 for r in results if r["result_status"] == "کامیاب")
    conditional_count = sum(1 for r in results if r["result_status"] == "مشروط")
    failed_count = sum(1 for r in results if r["result_status"] == "ناکام")
    mahroom_count = sum(1 for r in results if r["result_status"] == "محروم")
    mazrati_count = sum(1 for r in results if r["result_status"] == "معذرتی")

    avg_pct = round(sum(r["percentage"] for r in results) / total_students, 1) if total_students > 0 else 0.0
    pass_pct = round((passed_count / total_students * 100), 1) if total_students > 0 else 0.0

    top_three = passing_results[:3]

    stats = {
        "total_students": total_students,
        "passed_count": passed_count,
        "conditional_count": conditional_count,
        "failed_count": failed_count,
        "mahroom_count": mahroom_count,
        "mazrati_count": mazrati_count,
        "class_average_percentage": avg_pct,
        "pass_percentage": pass_pct,
        "top_three": top_three,
    }

    return {
        "class": class_obj,
        "academic_year": academic_year,
        "subjects": subjects,
        "students_results": results,
        "stats": stats,
    }


def seed_standard_curriculum_subjects():
    """
    Pre-assign standard subjects to existing classes according to Afghan education curriculum:
    - Primary (ابتدائیه: صنف ۱ تا ۶): قرآن کریم، دینیات، دری، پشتو، ریاضی، رسم و خط، تهذیب، تربیت بدنی
    - Middle (متوسطه: صنف ۷ تا ۹): قرآن، دینیات، دری، پشتو، انگلیسی، ریاضی، ساینس/فزیک، کیمیا، بیولوژی، تاریخ، جغرافیه، کمپیوتر، خط و رسم
    - Secondary (لیسه: صنف ۱۰ تا ۱۲): قرآن و تفسیر، دینیات، دری، پشتو، انگلیسی، ریاضیات، هندسه، فزیک، کیمیا، بیولوژی، تاریخ، جغرافیه، کمپیوتر
    """
    curriculum = [
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
        "حسن خط و رسم",
    ]

    for subj_name in curriculum:
        Subject.objects.get_or_create(name=subj_name)

    all_subjects = list(Subject.objects.all())
    for class_obj in Classes.objects.all():
        if class_obj.subjects.count() == 0:
            class_obj.subjects.set(all_subjects)
