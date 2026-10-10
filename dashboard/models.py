from django.db import models
import uuid
# Create your models here.


class Status(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="active")

    def __str__(self) -> str:
        return f"{self.name}"


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class Degree(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class Job(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class Province(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class District(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.province.name}-{self.name}"


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    school_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    gfname = models.CharField(max_length=50)
    card_id = models.CharField(max_length=50)
    birth_date = models.DateField(auto_now=False, auto_now_add=False)
    mother_language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    nationality = models.CharField(max_length=50)
    father_job = models.ForeignKey(Job, on_delete=models.DO_NOTHING)
    original_province = models.ForeignKey(
        Province, on_delete=models.DO_NOTHING, related_name="students_original")
    original_district = models.ForeignKey(
        District, on_delete=models.DO_NOTHING, related_name="students_original")
    original_zone = models.IntegerField()
    original_village = models.CharField(max_length=50)
    now_province = models.ForeignKey(
        Province, on_delete=models.DO_NOTHING, related_name="students_current")
    now_district = models.ForeignKey(
        District, on_delete=models.DO_NOTHING, related_name="students_current")
    now_zone = models.IntegerField()
    now_village = models.CharField(max_length=50)
    registered_date = models.DateField(auto_now=False, auto_now_add=False)
    detached_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    phone = models.CharField(max_length=13)
    status = models.ForeignKey(
        Status, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}-{self.fname}"


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    major = models.CharField(max_length=50)
    degree = models.ForeignKey(Degree, on_delete=models.DO_NOTHING)
    job = models.ForeignKey(Job, on_delete=models.DO_NOTHING)
    years_of_service = models.IntegerField()
    registered_date = models.DateField(auto_now=False, auto_now_add=False)
    detached_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True, blank=True)
    graduation_year = models.IntegerField()
    salary = models.IntegerField()
    tax = models.IntegerField()
    status = models.ForeignKey(
        Status, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.last_name}"


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class Month(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class ExamType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class AcademiceYear(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self) -> str:
        return f"{self.year}"


class Classes(models.Model):
    id = models.AutoField(primary_key=True)
    grade = models.IntegerField()
    alpha_grade = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    guidence = models.ForeignKey(
        Teacher, on_delete=models.DO_NOTHING, null=True, blank=True)
    # representative = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)
    # registered = models.IntegerField(default=0)
    capacity = models.IntegerField(default=30)
    start_time = models.TimeField(
        auto_now=False, auto_now_add=False, default="08:00")  # type: ignore
    end_time = models.TimeField(
        auto_now=False, auto_now_add=False, default="16:00")  # type: ignore
    turn = models.CharField(max_length=50, default="صبح")  # type: ignore
    status = models.ForeignKey(
        Status, on_delete=models.DO_NOTHING, default=1)  # type: ignore

    def __str__(self) -> str:
        return f"{self.grade}-{self.section}"

    def get_registered_count(self):
        return self.studentclass.count()

    def get_remaining_capacity(self):
        return self.capacity - self.get_registered_count()

    def get_registered_percentage(self):
        if self.capacity == 0:
            return 0
        return (self.get_registered_count() / self.capacity) * 100


class TeacherSubject(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.DO_NOTHING, related_name="teachersubject")
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    classs = models.ForeignKey(Classes, on_delete=models.DO_NOTHING)
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.teacher}-{self.subject}-{self.classs}"


class StudentClass(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.DO_NOTHING, related_name="studentclass")
    classs = models.ForeignKey(
        Classes, on_delete=models.DO_NOTHING, related_name="studentclass")
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.classs.grade}-{self.classs.section}"


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    classs = models.ForeignKey(Classes, on_delete=models.DO_NOTHING)
    month = models.ForeignKey(
        Month, on_delete=models.DO_NOTHING)
    present = models.IntegerField()

    absent = models.IntegerField()
    sick = models.IntegerField()
    excused = models.IntegerField()
    alldays = models.IntegerField()
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.student}-{self.classs}-{self.month}"

    def get_present_average(self):
        if self.alldays == 0:
            return 0
        return int((self.present / self.alldays) * 100)

    def get_absent_average(self):
        if self.alldays == 0:
            return 0
        return int((self.absent / self.alldays) * 100)

    def get_sick_average(self):
        if self.alldays == 0:
            return 0
        return int((self.sick / self.alldays) * 100)

    def get_excused_average(self):
        if self.alldays == 0:
            return 0
        return int((self.excused / self.alldays) * 100)

    def get_present_percentage(self):
        if self.alldays == 0:
            return 0
        return int((self.present / self.alldays) * 100)


class Assessment(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    classs = models.ForeignKey(Classes, on_delete=models.DO_NOTHING)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.DO_NOTHING)
    score = models.IntegerField()
    max_score = models.IntegerField()
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.student}-{self.teacher}-{self.subject}-{self.classs}-{self.month}"

    def getPercentage(self):
        return int((self.score/self.max_score)*100)

    def get_rank(self):
        # Get all assessments for the same subject, class, month, and academic year
        assessments = Assessment.objects.filter(
            subject=self.subject,
            classs=self.classs,
            month=self.month,
            academice_year=self.academice_year
        ).order_by('-score')

        # Create a list of scores
        scores = [assessment.score for assessment in assessments]

        # Get the rank of the current assessment
        rank = scores.index(self.score) + 1  # +1 because index starts at 0

        return rank

    def get_student_rank(self):
        p = self.getPercentage()
        if p == 100:
            return "نمره کامل"
        elif 90 <= p < 100:
            return "عالی"
        elif 80 <= p < 90:
            return "خوب"
        elif 60 <= p < 80:
            return "متوسط"
        else:
            return "ضعیف"


class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    classs = models.ForeignKey(Classes, on_delete=models.DO_NOTHING)
    exam_type = models.ForeignKey(ExamType, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.DO_NOTHING)
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self) -> str:
        return f"{self.teacher}-{self.classs}-{self.subject}-{self.month}"


class ExamResult(models.Model):
    id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    score = models.IntegerField()
    max_score = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.exam}-{self.student}-{self.score}"


class Fee(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    paied = models.IntegerField()
    payment_date = models.DateField(auto_now=False, auto_now_add=False)
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)


"""
class EducationalDay(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

class TimeTable(models.Model):
    id = models.AutoField(primary_key=True)
    day=models.ForeignKey(EducationalDay,on_delete=models.DO_NOTHING)
    hour=models.IntegerField()
    Subject=models.ForeignKey(Subject,  on_delete=models.DO_NOTHING)
    teacher=models.ForeignKey(Teacher,on_delete=models.DO_NOTHING)
    classs=models.ForeignKey(Classes,on_delete=models.DO_NOTHING)
"""
