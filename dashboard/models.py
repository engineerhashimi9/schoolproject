from django.conf import settings
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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
        verbose_name="حساب کاربری ورود"
    )
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
    @property
    def full_name(self):
        return f"{self.name} {self.fname} {self.last_name}"
    @property
    def total_salary(self):
        return self.salary - self.tax


class Subject(models.Model):
    CATEGORY_CHOICES = [
        ("علوم دینی و اسلامی", "علوم دینی و اسلامی"),
        ("زبان و ادبیات", "زبان و ادبیات"),
        ("علوم ساینسی و طبیعی", "علوم ساینسی و طبیعی"),
        ("ریاضیات و هندسه", "ریاضیات و هندسه"),
        ("علوم اجتماعی و بشری", "علوم اجتماعی و بشری"),
        ("فناوری، مهارت و هنر", "فناوری، مهارت و هنر"),
        ("تربیت بدنی و صحت", "تربیت بدنی و صحت"),
        ("سایر مضامین", "سایر مضامین"),
    ]

    LEVEL_CHOICES = [
        ("عمومی", "عمومی (تمام دوره‌ها)"),
        ("ابتدائیه", "دوره ابتدائیه (صنوف ۱ تا ۶)"),
        ("متوسطه", "دوره متوسطه (صنوف ۷ تا ۹)"),
        ("لیسه", "دوره لیسه (صنوف ۱۰ تا ۱۲)"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="نام مضمون")
    code = models.CharField(max_length=30, blank=True, null=True, verbose_name="کد مضمون")
    category = models.CharField(
        max_length=50,
        default="علوم ساینسی و طبیعی",
        choices=CATEGORY_CHOICES,
        verbose_name="دسته‌بندی نصاب"
    )
    educational_level = models.CharField(
        max_length=50,
        default="عمومی",
        choices=LEVEL_CHOICES,
        verbose_name="دوره تعلیمی"
    )
    weekly_hours = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="ساعات درسی در هفته"
    )
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=40.0,
        verbose_name="نمره کامیابی"
    )
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=100.0,
        verbose_name="مجموع نمره"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فعال"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="اهداف تعلیمی و توضیحات"
    )
    classes = models.ManyToManyField('Classes', blank=True, related_name="subjects")

    class Meta:
        verbose_name = "مضمون درسی"
        verbose_name_plural = "مضامین و نصاب تعلیمی"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def assigned_classes_count(self):
        return self.classes.count()

    @property
    def category_badge_class(self):
        cat_map = {
            "علوم دینی و اسلامی": "badge-islamic",
            "زبان و ادبیات": "badge-literature",
            "علوم ساینسی و طبیعی": "badge-science",
            "ریاضیات و هندسه": "badge-math",
            "علوم اجتماعی و بشری": "badge-social",
            "فناوری، مهارت و هنر": "badge-tech",
            "تربیت بدنی و صحت": "badge-sports",
        }
        return cat_map.get(self.category, "badge-default")


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
    academice_year = models.ForeignKey(
        AcademiceYear, on_delete=models.DO_NOTHING)
    capacity = models.IntegerField(default=30)
    start_time = models.TimeField(
        auto_now=False, auto_now_add=False, default="08:00")  
    end_time = models.TimeField(
        auto_now=False, auto_now_add=False, default="16:00")
    turn = models.CharField(max_length=50, default="صبح")  
    status = models.ForeignKey(
        Status, on_delete=models.DO_NOTHING, default=1)  

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
        if not self.max_score or self.max_score <= 0:
            return 0
        return int((self.score / self.max_score) * 100)

    def get_rank(self):
        assessments = Assessment.objects.filter(
            subject=self.subject,
            classs=self.classs,
            month=self.month,
            academice_year=self.academice_year
        ).order_by('-score')

        scores = [assessment.score for assessment in assessments]
        try:
            rank = scores.index(self.score) + 1
        except ValueError:
            rank = 1
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
    def getPercentage(self):
        if not self.max_score or self.max_score <= 0:
            return 0
        return int((self.score / self.max_score) * 100)
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
    
    
class ExamMark(models.Model):
    # shoqqa
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="exam_marks")
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name="exam_marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="exam_marks")
    academice_year = models.ForeignKey(AcademiceYear, on_delete=models.CASCADE, related_name="exam_marks")

    midterm_marks = models.DecimalField(max_digits=5, decimal_places=1, default=0, null=True, blank=True)
    final_marks = models.DecimalField(max_digits=5, decimal_places=1, default=0, null=True, blank=True)
    conditional_marks = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    is_mahroom = models.BooleanField(default=False)
    is_mazrati = models.BooleanField(default=False)
    notes = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'classs', 'subject', 'academice_year')
        verbose_name = "نمره امتحان (شقه)"
        verbose_name_plural = "شقه نمرات امتحانات"

    def __str__(self) -> str:
        return f"{self.student.name} - {self.subject.name}: {self.total_marks}"

    @property
    def total_marks(self):
        m = float(self.midterm_marks or 0)
        f = float(self.final_marks or 0)
        return round(m + f, 1)

    @property
    def effective_marks(self):
        if self.conditional_marks is not None:
            return round(float(self.conditional_marks), 1)
        return self.total_marks

    @property
    def is_midterm_passed(self):
        return float(self.midterm_marks or 0) >= 16.0

    @property
    def is_final_passed(self):
        return float(self.final_marks or 0) >= 24.0

    @property
    def is_passed(self):
        if self.is_mahroom or self.is_mazrati:
            return False
        if self.conditional_marks is not None:
            return float(self.conditional_marks) >= 40.0
        return self.total_marks >= 40.0 and self.is_final_passed

    @property
    def status_label(self):
        if self.is_mahroom:
            return "محروم"
        if self.is_mazrati:
            return "معذرتی"
        if self.conditional_marks is not None:
            return "کامیاب (مشروطی)" if float(self.conditional_marks) >= 40.0 else "ناکام"
        if self.is_passed:
            return "کامیاب"
        return "ناکام"


Shaqqa = ExamMark


class ExamAttendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="exam_attendances")
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name="exam_attendances")
    academice_year = models.ForeignKey(AcademiceYear, on_delete=models.CASCADE, related_name="exam_attendances")

    # Midterm period attendance (چهارونیم ماهه)
    midterm_present = models.IntegerField(default=0)
    midterm_absent = models.IntegerField(default=0)
    midterm_sick = models.IntegerField(default=0)
    midterm_leave = models.IntegerField(default=0)

    # Final period attendance (سالانه)
    final_present = models.IntegerField(default=0)
    final_absent = models.IntegerField(default=0)
    final_sick = models.IntegerField(default=0)
    final_leave = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'classs', 'academice_year')
        verbose_name = "حاضری امتحانات"
        verbose_name_plural = "ضوابط حاضری امتحانات"

    def __str__(self) -> str:
        return f"{self.student.name} - حاضری امتحانات {self.classs}"

    @property
    def total_present(self):
        return (self.midterm_present or 0) + (self.final_present or 0)

    @property
    def total_absent(self):
        return (self.midterm_absent or 0) + (self.final_absent or 0)

    @property
    def total_sick(self):
        return (self.midterm_sick or 0) + (self.final_sick or 0)

    @property
    def total_leave(self):
        return (self.midterm_leave or 0) + (self.final_leave or 0)

    @property
    def total_days(self):
        return self.total_present + self.total_absent + self.total_sick + self.total_leave
    
        


class Fee(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    class_section = models.ForeignKey(Classes, on_delete=models.DO_NOTHING, null=True, blank=True)
    month: models.ForeignKey = models.ForeignKey(Month, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    paied = models.IntegerField()
    payment_date = models.DateField(auto_now=False, auto_now_add=False)
    academice_year = models.ForeignKey(AcademiceYear, on_delete=models.DO_NOTHING)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default="نقدی", blank=True)
    fee_category = models.CharField(max_length=50, default="شهریه ماهوار", blank=True)
    notes = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.student} - {self.month}: {self.paied}/{self.amount}"

    def get_status(self):
        if self.amount == self.paied:
            return 1
        return 0

    def get_percent(self):
        if not self.amount or self.amount <= 0:
            return 0
        return int((self.paied / self.amount) * 100)

    @property
    def remaining(self):
        return max(0, (self.amount or 0) - (self.paied or 0))

    @property
    def status_label(self):
        if (self.paied or 0) >= (self.amount or 0):
            return "تسویه کامل"
        elif (self.paied or 0) > 0:
            return "پرداخت قسطی"
        return "معوقه و بدهکار"

    @property
    def status_class(self):
        if (self.paied or 0) >= (self.amount or 0):
            return "badge-active"
        elif (self.paied or 0) > 0:
            return "badge-warning"
        return "badge-inactive"


class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100, default="متفرقه")
    title = models.CharField(max_length=200)
    amount = models.IntegerField()
    payment_date = models.DateField()
    recipient = models.CharField(max_length=150, blank=True, null=True)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default="نقدی", blank=True)
    academice_year = models.ForeignKey(AcademiceYear, on_delete=models.DO_NOTHING, null=True, blank=True)
    month = models.ForeignKey(Month, on_delete=models.DO_NOTHING, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "مصرف مکتب"
        verbose_name_plural = "مصارف و مخارج مکتب"

    def __str__(self):
        return f"{self.title} - {self.amount} AFN"


class TimeTable(models.Model):
    DAY_CHOICES = [
        (1, "شنبه"),
        (2, "یک‌شنبه"),
        (3, "دوشنبه"),
        (4, "سه‌شنبه"),
        (5, "چهارشنبه"),
        (6, "پنج‌شنبه"),
    ]

    PERIOD_CHOICES = [
        (1, "ساعت اول"),
        (2, "ساعت دوم"),
        (3, "ساعت سوم"),
        (4, "ساعت چهارم"),
        (5, "ساعت پنجم"),
        (6, "ساعت ششم"),
    ]

    DAY_NAMES = {
        1: "شنبه",
        2: "یک‌شنبه",
        3: "دوشنبه",
        4: "سه‌شنبه",
        5: "چهارشنبه",
        6: "پنج‌شنبه",
    }

    PERIOD_NAMES = {
        1: "ساعت اول",
        2: "ساعت دوم",
        3: "ساعت سوم",
        4: "ساعت چهارم",
        5: "ساعت پنجم",
        6: "ساعت ششم",
    }

    PERIOD_TIMES = {
        1: "۰۸:۰۰ - ۰۸:۴۵",
        2: "۰۸:۴۵ - ۰۹:۳۰",
        3: "۰۹:۳۰ - ۱۰:۱۵",
        4: "۱۰:۳۵ - ۱۱:۲۰",
        5: "۱۱:۲۰ - ۱۲:۰۵",
        6: "۱۲:۰۵ - ۱۲:۵۰",
    }

    id = models.AutoField(primary_key=True)
    classs = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name="timetables")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="timetables")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetables")
    academic_year = models.ForeignKey(AcademiceYear, on_delete=models.CASCADE, related_name="timetables")
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    period = models.PositiveSmallIntegerField(choices=PERIOD_CHOICES)
    room_number = models.CharField(max_length=50, blank=True, null=True, default="اتاق صنف")
    notes = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "تقسیم اوقات"
        verbose_name_plural = "تقسیم اوقات درسی مکتب"
        ordering = ["academic_year", "classs", "day_of_week", "period"]
        constraints = [
            models.UniqueConstraint(
                fields=["classs", "day_of_week", "period", "academic_year"],
                name="unique_class_timetable_slot"
            ),
            models.UniqueConstraint(
                fields=["teacher", "day_of_week", "period", "academic_year"],
                name="unique_teacher_timetable_slot"
            ),
        ]

    def __str__(self):
        return f"{self.classs} - {self.day_name} {self.period_name}: {self.subject} ({self.teacher})"

    @property
    def day_name(self):
        return self.DAY_NAMES.get(self.day_of_week, "")

    @property
    def period_name(self):
        return self.PERIOD_NAMES.get(self.period, "")

    @property
    def period_time(self):
        return self.PERIOD_TIMES.get(self.period, "")

