from django.forms import modelformset_factory
d = {
    "Alice": 28,
    "Blice": 70,
    "Bob": 35,
    "Charlie": 28,
    "Diana": 41
}
nd = {}
l = list(d.values())
l.sort()
v = list(d.keys())
for i in l:
    for j in d:
        if d[j] == i:
            if i in nd.values():
                pass

            else:
                nd[j] = i
            del d[j]
            break
print(nd)


AttendanceFormSet = modelformset_factory(
    Attendance,
    fields=("present", "absent", "sick", "excused", "alldays"),
    extra=0
)
@login_required
def attendance_edit(request, class_id, month_id, academic_year_id):
    class_obj = get_object_or_404(Classes, id=class_id)
    month = get_object_or_404(Month, id=month_id)
    academic_year = get_object_or_404(AcademiceYear, id=academic_year_id)

    records = Attendance.objects.filter(
        classs=class_obj,
        month=month,
        academice_year=academic_year
    ).select_related("student")

    if request.method == "POST":
        for record in records:
            record.present = int(request.POST.get(f"present_{record.student_id}", 0))
            record.absent = int(request.POST.get(f"absent_{record.student_id}", 0))
            record.sick = int(request.POST.get(f"sick_{record.student_id}", 0))
            record.excused = int(request.POST.get(f"excused_{record.student_id}", 0))
            record.alldays = int(request.POST.get(f"alldays_{record.student_id}", 25))
            record.present_percent = round((record.present / record.alldays * 100), 2) if record.alldays else 0
            record.save()

        return HttpResponseRedirect(reverse("dashboard:attendence-list"))

    context = {
        "records": records,
        "class_obj": class_obj,
        "month": month,
        "academic_year": academic_year,
    }
    return render(request, "dashboard/attendence/attendance_edit.html", context)
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from dashboard.models import StudentClass, Attendance, Classes, Month, AcademiceYear

@login_required
def attendance_add(request, class_id, month_id, academic_year_id):
    class_obj = get_object_or_404(Classes, id=class_id)
    month = get_object_or_404(Month, id=month_id)
    academic_year = get_object_or_404(AcademiceYear, id=academic_year_id)

    students = StudentClass.objects.filter(classs=class_obj, academice_year=academic_year).select_related("student")

    if request.method == "POST":
        for item in students:
            student = item.student
            present = int(request.POST.get(f"present_{student.id}", 0))
            absent = int(request.POST.get(f"absent_{student.id}", 0))
            sick = int(request.POST.get(f"sick_{student.id}", 0))
            excused = int(request.POST.get(f"excused_{student.id}", 0))
            alldays = int(request.POST.get(f"alldays_{student.id}", 25))

            Attendance.objects.update_or_create(
                student=student,
                classs=class_obj,
                month=month,
                academice_year=academic_year,
                defaults={
                    "present": present,
                    "absent": absent,
                    "sick": sick,
                    "excused": excused,
                    "alldays": alldays,
                    "present_percent": round((present / alldays * 100), 2) if alldays else 0,
                }
            )

        return HttpResponseRedirect(reverse("dashboard:attendence-list"))

    context = {
        "class_obj": class_obj,
        "month": month,
        "academic_year": academic_year,
        "students": students,
    }
    return render(request, "dashboard/attendence/attendance_add.html", context)