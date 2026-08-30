from django.db import models

# Create your models here.


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id}-{self.name}"


class Degree(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.id}-{self.name}"


class Job(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id}-{self.name}"


class Province(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id}-{self.name}"


class District(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}-{self.name}"


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
    detached_date = models.DateField(auto_now=False, auto_now_add=False)
    phone = models.CharField(max_length=13)


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
    detached_date = models.DateField(auto_now=False, auto_now_add=False)
    graduation_year = models.IntegerField()
    salary = models.IntegerField()
    tax = models.IntegerField()

    def __str__(self):
        return f"{self.name}-{self.fname}-{self.last_name}"


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Month(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class ExamType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class AcademicYear(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)


class Classes(models.Model):
    id = models.AutoField(primary_key=True)
    grade = models.IntegerField()
    section = models.CharField(max_length=50)
    guidence = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)


class TeacherSubject(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)


class StudentClass(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name="studentclass")
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


class ExamResult(models.Model):
    id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField()


class Fee(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month: models.ForeignKey = models.ForeignKey(
        Month, on_delete=models.CASCADE)
    amount = models.IntegerField()
    paied = models.IntegerField()
    payment_date = models.DateField(auto_now=False, auto_now_add=False)
    academice_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)


