from django.urls import path
from . import views
app_name = "dashboard"

urlpatterns = [
    # main dashboard
    path("", views.dashboard_view, name="admin-dashboard"),

    # student urls
    path("student/", views.StudentListView.as_view(), name="student-list"),
    path("student/create", views.student_create, name="student-register"),
    path("student/<int:pk>", views.StudentDetailView.as_view(),
         name="student-detail"),
    path("student/<int:id>/disable", views.disable_student, name="student-disable"),
    path("student/<int:id>/edite", views.student_edite, name="student-edite"),

    # worker urls
    path("worker/", views.TeacherListView.as_view(), name="worker-list"),
    path("worker/create", views.teacher_create, name="worker-register"),
    path("worker/<int:pk>", views.TeacherDetailView.as_view(), name="worker-detail"),
    path("worker/<int:id>/edite", views.teacher_edite, name="worker-edite"),
    path("worker/<int:id>/disable", views.disable_teacher, name="worker-disable"),

    # classes urls
    path("class/", views.ClassesListView.as_view(), name="class-list"),
    path("class/<int:pk>", views.ClassDetailView.as_view(), name="class-detail"),
    path("class/<int:id>/edite", views.class_edite, name="class-edite"),
    path("class/create", views.class_create, name="class-register"),
    path("class/<int:id>/disable", views.class_disable, name="class-disable"),
    # attendence urls
    path("attendence/", views.AttendenceListView.as_view(), name="attendence-list"),
    path("attendence/create/", views.attendence_create, name="attendence-create"),
    path("attendence/edite/", views.attendence_edite, name="attendence-edite"),
    path("attendence/edite/<int:class_id>/<int:month_id>/<int:academic_year_id>/", views.attendence_edite, name="attendence-edite-specific"),

    # assesment urls
    path("assesment/", views.AssesmentListView.as_view(), name="assesment-list"),
    path("assesment/create/", views.assesment_create, name="assesment-create"),
    path("assesment/<int:id>/edite/", views.assesment_edite, name="assesment-edite"),
    path("assesment/<int:id>/delete/", views.assesment_delete, name="assesment-delete"),
    # exam & grading management urls (امتحانات و نتایج وزارت معارف)
    path("exam/", views.exam_dashboard_view, name="exam-list"),
    path("exam/dashboard/", views.exam_dashboard_view, name="exam-dashboard"),
    path("exam/shaqqa/", views.shaqqa_entry_view, name="exam-shaqqa"),
    path("exam/jadwal-nataij/", views.jadwal_nataij_view, name="exam-jadwal-nataij"),
    path("exam/etlanama/", views.etlanama_view, name="exam-etlanama"),
    path("exam/etlanama/<int:student_id>/", views.etlanama_view, name="exam-etlanama-student"),
    path("exam/attendance/", views.exam_attendance_view, name="exam-attendance"),
    path("exam/subjects/", views.exam_subjects_view, name="exam-subjects"),
    # finance urls (امور مالی، شهریه و مصارف مکتب)
    path("finance/", views.FinanceListView.as_view(), name="finance-list"),
    path("finance/create/", views.fee_create, name="fee-create"),
    path("finance/<int:id>/edite/", views.fee_edite, name="fee-edite"),
    path("finance/<int:id>/delete/", views.fee_delete, name="fee-delete"),
    path("finance/<int:id>/receipt/", views.fee_receipt_view, name="fee-receipt"),
    path("finance/expenses/", views.expenses_view, name="finance-expenses"),
    path("finance/expenses/<int:id>/delete/", views.expense_delete, name="expense-delete"),
    path("finance/report/", views.finance_report_view, name="finance-report"),
    # timetable urls (تقسیم اوقات درسی صنوف و اساتید)
    path("timetable/class/", views.timetable_class_view, name="timetable-class"),
    path("timetable/teacher/", views.timetable_teacher_view, name="timetable-teacher"),
    path("timetable/master/", views.timetable_master_view, name="timetable-master"),
    path("timetable/slot/save/", views.timetable_slot_save, name="timetable-slot-save"),
    path("timetable/slot/<int:id>/delete/", views.timetable_slot_delete, name="timetable-slot-delete"),
    path("timetable/class/<int:class_id>/print/", views.timetable_class_print, name="timetable-class-print"),
    path("timetable/teacher/<int:teacher_id>/print/", views.timetable_teacher_print, name="timetable-teacher-print"),
    # Subject & Afghan Curriculum Management URLs (مدیریت مضامین و نصاب تعلیمی)
    path("subjects/", views.subject_list_view, name="subject-list"),
    path("subjects/create/", views.subject_create_view, name="subject-create"),
    path("subjects/<int:id>/", views.subject_detail_view, name="subject-detail"),
    path("subjects/<int:id>/edit/", views.subject_edit_view, name="subject-edit"),
    path("subjects/<int:id>/delete/", views.subject_delete_view, name="subject-delete"),
    path("subjects/<int:id>/toggle-status/", views.subject_toggle_status_view, name="subject-toggle-status"),
    path("subjects/class-matrix/", views.subject_class_matrix_view, name="subject-class-matrix"),
    path("subjects/class/<int:class_id>/print/", views.subject_class_print_view, name="subject-class-print"),
    # Teacher Dashboard & Management URLs (پورتال و مدیریت اختصاصی اساتید)
    path("teacher/", views.teacher_portal_view, name="teacher-portal"),
    path("teacher/attendance/", views.teacher_attendance_view, name="teacher-attendance"),
    path("teacher/assessment/", views.teacher_assessment_view, name="teacher-assessment"),
    path("teacher/shaqqa/", views.teacher_shaqqa_view, name="teacher-shaqqa"),
    path("teacher/timetable/my/", views.teacher_my_timetable_view, name="teacher-my-timetable"),
    path("teacher/timetable/class/", views.teacher_class_timetable_view, name="teacher-class-timetable"),
    path("teacher/students/", views.teacher_students_view, name="teacher-students"),
]

