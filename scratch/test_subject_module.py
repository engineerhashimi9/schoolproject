import os
import sys
import django

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from dashboard.models import Subject, Classes, ExamMark, AcademiceYear
from dashboard.services.subject_service import (
    get_afghan_curriculum_standards,
    apply_afghan_curriculum_to_class,
    get_subject_statistics,
    get_subject_detail_metrics,
    validate_subject_deletion,
    get_class_educational_stage,
)

User = get_user_model()

def test_subject_module():
    print("==================================================")
    print("STARTING SUBJECT & CURRICULUM MANAGEMENT TESTS")
    print("==================================================")

    # 1. Model & Service Logic
    print("\n--- 1. Testing Afghan Curriculum Standards & Service ---")
    standards = get_afghan_curriculum_standards()
    assert "ابتدائیه" in standards, "Missing ابتدائیه"
    assert "متوسطه" in standards, "Missing متوسطه"
    assert "لیسه" in standards, "Missing لیسه"
    print(f"✓ MoE Curriculum Standards: Primary={len(standards['ابتدائیه'])}, Middle={len(standards['متوسطه'])}, High={len(standards['لیسه'])}")

    cls_10 = Classes.objects.filter(grade=10).first() or Classes.objects.first()
    stage = get_class_educational_stage(cls_10)
    print(f"✓ Class {cls_10.grade}-{cls_10.section} stage: {stage}")

    res = apply_afghan_curriculum_to_class(cls_10)
    assert res["assigned_count"] > 0, "Curriculum assignment failed"
    print(f"✓ Applied standard MoE curriculum to {cls_10}: {res['assigned_count']} subjects assigned.")

    stats = get_subject_statistics()
    print(f"✓ Subject Statistics: Total={stats['total_subjects']}, Active={stats['active_subjects']}, Hours={stats['total_weekly_hours']}")
    assert stats["total_subjects"] >= 15, "Too few subjects"

    # 2. Subject Deletion Safety Validation
    print("\n--- 2. Testing Deletion Safety Validation ---")
    active_subj = Subject.objects.filter(exam_marks__isnull=False).first()
    if active_subj:
        val = validate_subject_deletion(active_subj)
        assert not val["can_delete"], "Should NOT allow deleting subject with exam marks!"
        print(f"✓ Protected Subject with Marks: «{active_subj.name}» (Can Delete: {val['can_delete']})")

    dummy_subj, _ = Subject.objects.get_or_create(
        name="مضمون تستی آزمایشی",
        code="TST-999",
        category="سایر مضامین",
        educational_level="عمومی",
        weekly_hours=2,
    )
    val_dummy = validate_subject_deletion(dummy_subj)
    assert val_dummy["can_delete"], "Dummy subject without marks should be safely deletable!"
    print(f"✓ Unused Subject Deletable: «{dummy_subj.name}» (Can Delete: {val_dummy['can_delete']})")

    # 3. Authenticated Client Views Testing
    print("\n--- 3. Testing Subject HTTP Views with Client ---")
    client = Client()
    admin_user = User.objects.filter(is_staff=True).first()
    client.force_login(admin_user)

    # 3.1 List View
    url_list = reverse("dashboard:subject-list")
    resp = client.get(url_list)
    assert resp.status_code == 200, f"Subject list failed: {resp.status_code}"
    print(f"✓ [200] Subject List: {url_list}")

    # Search & Filters
    resp_search = client.get(f"{url_list}?search=فزیک")
    assert resp_search.status_code == 200
    resp_cat = client.get(f"{url_list}?category=علوم دینی و اسلامی")
    assert resp_cat.status_code == 200
    resp_lvl = client.get(f"{url_list}?level=لیسه")
    assert resp_lvl.status_code == 200
    resp_stat = client.get(f"{url_list}?status=active")
    assert resp_stat.status_code == 200
    print("✓ [200] Subject Search & Filter queries verified.")

    # 3.2 Create View GET & POST
    url_create = reverse("dashboard:subject-create")
    resp_create_get = client.get(url_create)
    assert resp_create_get.status_code == 200
    print(f"✓ [200] Subject Create GET: {url_create}")

    resp_create_post = client.post(url_create, {
        "name": "روان‌شناسی تعلیمی و تربیتی",
        "code": "PSY-201",
        "category": "علوم اجتماعی و بشری",
        "educational_level": "لیسه",
        "weekly_hours": 2,
        "passing_score": 40.0,
        "total_score": 100.0,
        "is_active": True,
        "description": "اصول روانشناسی یادگیری و تربیت اسلامی.",
        "classes": [cls_10.id],
    })
    assert resp_create_post.status_code == 302, f"Subject create POST failed: {resp_create_post.status_code}"
    created_subj = Subject.objects.filter(code="PSY-201").first()
    assert created_subj is not None, "Subject was not created in DB!"
    print(f"✓ [302] Subject Create POST: Created «{created_subj.name}» successfully.")

    # 3.3 Detail View
    url_detail = reverse("dashboard:subject-detail", kwargs={"id": created_subj.id})
    resp_detail = client.get(url_detail)
    assert resp_detail.status_code == 200
    print(f"✓ [200] Subject Detail: {url_detail}")

    # 3.4 Edit View GET & POST
    url_edit = reverse("dashboard:subject-edit", kwargs={"id": created_subj.id})
    resp_edit_get = client.get(url_edit)
    assert resp_edit_get.status_code == 200
    print(f"✓ [200] Subject Edit GET: {url_edit}")

    resp_edit_post = client.post(url_edit, {
        "name": "روان‌شناسی تعلیمی و تربیتی (ویرایش‌شده)",
        "code": "PSY-201-REV",
        "category": "علوم اجتماعی و بشری",
        "educational_level": "لیسه",
        "weekly_hours": 3,
        "passing_score": 40.0,
        "total_score": 100.0,
        "is_active": True,
        "description": "ویرایش سرفصل‌ها.",
        "classes": [cls_10.id],
    })
    assert resp_edit_post.status_code == 302
    created_subj.refresh_from_db()
    assert created_subj.code == "PSY-201-REV"
    print(f"✓ [302] Subject Edit POST: Updated to «{created_subj.name}»")

    # 3.5 Toggle Status View
    url_toggle = reverse("dashboard:subject-toggle-status", kwargs={"id": created_subj.id})
    resp_toggle = client.get(url_toggle)
    assert resp_toggle.status_code == 302
    created_subj.refresh_from_db()
    assert created_subj.is_active is False
    print(f"✓ [302] Subject Toggle Status: Inactive now ({created_subj.is_active})")

    # 3.6 Class Matrix View GET & POST
    url_matrix = reverse("dashboard:subject-class-matrix")
    resp_matrix_get = client.get(url_matrix)
    assert resp_matrix_get.status_code == 200
    print(f"✓ [200] Subject Class Matrix GET: {url_matrix}")

    resp_matrix_post = client.post(url_matrix, {
        "action_type": "save_custom",
        "class_id": cls_10.id,
        "subject_ids": [s.id for s in Subject.objects.all()[:5]],
    })
    assert resp_matrix_post.status_code == 302
    print(f"✓ [302] Subject Class Matrix Custom Save: Saved subjects for {cls_10}")

    resp_matrix_moe = client.post(url_matrix, {
        "action_type": "apply_standard",
        "class_id": cls_10.id,
        "curriculum_stage": "لیسه",
    })
    assert resp_matrix_moe.status_code == 302
    print(f"✓ [302] Subject Class Matrix MoE Standard Apply: Applied MoE standard to {cls_10}")

    # 3.7 Class Curriculum Print View
    url_print = reverse("dashboard:subject-class-print", kwargs={"class_id": cls_10.id})
    resp_print = client.get(url_print)
    assert resp_print.status_code == 200
    print(f"✓ [200] Class Curriculum Print A4: {url_print}")

    # 3.8 Delete View
    url_delete = reverse("dashboard:subject-delete", kwargs={"id": created_subj.id})
    resp_delete = client.get(url_delete)
    assert resp_delete.status_code == 302
    assert not Subject.objects.filter(id=created_subj.id).exists()
    print(f"✓ [302] Subject Delete: Safely deleted test subject.")

    # Clean up dummy
    if Subject.objects.filter(id=dummy_subj.id).exists():
        dummy_subj.delete()

    print("\n==================================================")
    print("ALL SUBJECT & CURRICULUM MANAGEMENT TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_subject_module()
