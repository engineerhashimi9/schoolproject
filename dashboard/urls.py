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
]
