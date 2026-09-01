from django.db import models

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
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"


class Student(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    gfname = models.CharField(max_length=50)
    card_id = models.CharField(max_length=50)
    birth_date = models.DateField(auto_now=False, auto_now_add=False)
    mother_language = models.ForeignKey(Language, on_delete=models.CASCADE)
    nationality = models.CharField(max_length=50)
    father_job = models.ForeignKey(Job, on_delete=models.CASCADE)
    original_province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="students_original")
    original_district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="students_original")
    orignial_zone = models.IntegerField()
    original_village = models.CharField(max_length=50)
    now_province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="students_current")
    now_district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="students_current")
    now_zone = models.IntegerField()
    now_village = models.CharField(max_length=50)
    registered_date = models.DateField(auto_now=False, auto_now_add=False)
    detached_date = models.DateField(auto_now=False, auto_now_add=False,null=True,blank=True)
    phone = models.CharField(max_length=13)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self) -> str:
        return f"{self.name}-{self.fname}"


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    major = models.CharField(max_length=50)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    years_of_service = models.IntegerField()
    registered_date = models.DateField(auto_now=False, auto_now_add=False)
    detached_date = models.DateField(auto_now=False, auto_now_add=False,null=True,blank=True)
    graduation_year = models.IntegerField()
    salary = models.IntegerField()
    tax = models.IntegerField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True,blank=True)

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


class AcademicYear(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self) -> str:
        return f"{self.year}"


class Classes(models.Model):
    id = models.AutoField(primary_key=True)
    grade = models.IntegerField()
    section = models.CharField(max_length=50)
    guidence = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.grade}-{self.section}"


class TeacherSubject(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.teacher}-{self.subject}-{self.classs}"


class StudentClass(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="studentclass")
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.classs.grade}-{self.classs.section}"


class Atendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE)
    month = models.ForeignKey(
        Month, on_delete=models.CASCADE)
    present = models.IntegerField()
    absent = models.IntegerField()
    sick = models.IntegerField()
    excused = models.IntegerField()
    alldays = models.IntegerField()
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.student}-{self.classs}-{self.month}"


class Assessment(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField()
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.student}-{self.teacher}-{self.subject}-{self.classs}-{self.month}"


class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.CASCADE)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self) -> str:
        return f"{self.teacher}-{self.classs}-{self.subject}-{self.month}"


class ExamResult(models.Model):
    id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.exam}-{self.student}-{self.score}"


class Fee(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.CASCADE)
    amount = models.IntegerField()
    paied = models.IntegerField()
    payment_date = models.DateField(auto_now=False, auto_now_add=False)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
