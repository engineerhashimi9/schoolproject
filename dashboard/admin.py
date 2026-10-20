from django.contrib import admin
from .models import *


admin.site.register(Language)
admin.site.register(Degree)
admin.site.register(Job)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Student)
admin.site.register(Teacher)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "category",
        "educational_level",
        "weekly_hours",
        "passing_score",
        "total_score",
        "is_active",
    )
    list_filter = ("category", "educational_level", "is_active")
    search_fields = ("name", "code", "description")
    filter_horizontal = ("classes",)


admin.site.register(Month)
admin.site.register(ExamType)
admin.site.register(AcademiceYear)
admin.site.register(Classes)
admin.site.register(TeacherSubject)
admin.site.register(StudentClass)
admin.site.register(Attendance)
admin.site.register(Assessment)
admin.site.register(Exam)
admin.site.register(ExamResult)
admin.site.register(Fee)
admin.site.register(Status)
admin.site.register(ExamMark)
admin.site.register(ExamAttendance)
admin.site.register(Expense)
admin.site.register(TimeTable)
