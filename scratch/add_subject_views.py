import os

views_path = os.path.join("dashboard", "views.py")

with open(views_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
old_import = "from .forms import StudentForm, TeacherForm, ClassForm"
new_import = """from .forms import StudentForm, TeacherForm, ClassForm, SubjectForm
from .services.subject_service import (
    get_afghan_curriculum_standards,
    apply_afghan_curriculum_to_class,
    get_subject_statistics,
    get_subject_detail_metrics,
    validate_subject_deletion,
    get_class_educational_stage,
)"""

if old_import in content:
    content = content.replace(old_import, new_import, 1)
    print("Updated imports in views.py")
else:
    print("Warning: old_import not found")

# 2. Append new subject views
subject_views_code = """

# -----------------------------------------------------------------------------
#####
#####
######### -------------- Subject & Afghan Curriculum Management SECTION --------------###
#####
#####
# ---------------------------------------------------------------------------

@is_admin
def subject_list_view(request):
    \"\"\"
    Academic Curriculum & Subject Directory (فهرست مضامین و مدیریت نصاب تعلیمی معارف).
    \"\"\"
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
    \"\"\"
    Create a new curriculum subject (تعریف مضمون رسمی جدید در نصاب تعلیمی).
    \"\"\"
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
            messages.error(request, "لطفاً خطاهای فرم ثبت مضمون را بررسی و اصلاح فرمایید.")
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
    \"\"\"
    Edit curriculum subject details (ویرایش و اصلاح مشخصات مضمون تعلیمی).
    \"\"\"
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
            messages.error(request, "لطفاً خطاهای فرم ویرایش مضمون را بررسی فرمایید.")
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
    \"\"\"
    Detailed Profile of an Academic Subject (مشخصات و آمار تحلیلی مضمون).
    \"\"\"
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
    \"\"\"
    Toggle Active / Inactive status of a subject (فعال / غیرفعال‌سازی در نصاب).
    \"\"\"
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
    \"\"\"
    Safe Deletion of a Subject with Integrity Protection (حذف ایمن مضمون).
    \"\"\"
    subject = get_object_or_404(Subject, id=id)
    validation = validate_subject_deletion(subject)

    if not validation["can_delete"]:
        messages.warning(request, validation["reason"])
        return redirect(reverse("dashboard:subject-list"))

    subj_name = subject.name
    subject.delete()
    messages.success(request, f"مضمون «{subj_name}» با موفقیت از سیستم حذف گردید.")
    return redirect(reverse("dashboard:subject-list"))


@is_admin
def subject_class_matrix_view(request):
    \"\"\"
    Class Curriculum Assignment Matrix & Bulk Afghan MoE Standards Application
    (ماتریس تخصیص مضامین به صنوف و اِعمال نصاب معیاری وزارت معارف).
    \"\"\"
    classes = Classes.objects.all().order_by("grade", "section")
    all_subjects = Subject.objects.all().order_by("category", "name")

    selected_class_id = request.GET.get("class_id") or request.POST.get("class_id")
    selected_class = (
        Classes.objects.filter(id=int(selected_class_id)).first()
        if selected_class_id and str(selected_class_id).isdigit()
        else (Classes.objects.filter(grade=10, section="الف").first() or classes.first())
    )

    if request.method == "POST" and selected_class:
        action_type = request.POST.get("action_type")

        if action_type == "apply_standard":
            stage = request.POST.get("curriculum_stage") or get_class_educational_stage(selected_class)
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

    current_assigned_ids = set(selected_class.subjects.values_list("id", flat=True)) if selected_class else set()
    current_weekly_hours = sum(s.weekly_hours for s in selected_class.subjects.all()) if selected_class else 0
    educational_stage = get_class_educational_stage(selected_class) if selected_class else "لیسه"

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
    \"\"\"
    Official Class Curriculum & Syllabus Sheet (مفردات و جدول مضامین رسمی صنف) - A4 Print Layout.
    \"\"\"
    cls = get_object_or_404(Classes, id=class_id)
    year_id = request.GET.get("year_id")
    if year_id and str(year_id).isdigit():
        year = AcademiceYear.objects.filter(id=int(year_id)).first()
    else:
        year = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()

    subjects = list(cls.subjects.all().order_by("category", "name"))
    total_hours = sum(s.weekly_hours for s in subjects)

    # Attach teacher info from TimeTable or TeacherSubject
    subject_rows = []
    for s in subjects:
        tt_slot = TimeTable.objects.filter(classs=cls, subject=s).first()
        ts_rec = TeacherSubject.objects.filter(classs=cls, subject=s).first()
        teacher = tt_slot.teacher if tt_slot else (ts_rec.teacher if ts_rec else None)
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
"""

content += subject_views_code

with open(views_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Added subject views to dashboard/views.py")
