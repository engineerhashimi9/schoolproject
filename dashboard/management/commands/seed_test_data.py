from datetime import date

from django.core.management.base import BaseCommand

from dashboard.models import (
    AcademiceYear,
    Assessment,
    Attendance,
    Classes,
    Degree,
    District,
    Exam,
    ExamResult,
    ExamType,
    Fee,
    Job,
    Language,
    Month,
    Province,
    Status,
    Student,
    StudentClass,
    Subject,
    Teacher,
    TeacherSubject,
)


class Command(BaseCommand):
    help = "Seed the school database with Persian/Afghan sample records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of student records to create.",
        )

    def clear_existing_data(self):
        for model in [
            Fee,
            ExamResult,
            Assessment,
            Attendance,
            StudentClass,
            TeacherSubject,
            Exam,
            Classes,
            Teacher,
            Student,
            District,
            Province,
            Status,
            Language,
            Degree,
            Job,
            AcademiceYear,
            Subject,
            Month,
            ExamType,
        ]:
            model.objects.all().delete()

    def handle(self, *args, **options):
        count = max(1, options["count"])
        self.clear_existing_data()

        status_active, _ = Status.objects.get_or_create(name="فعال")
        status_inactive, _ = Status.objects.get_or_create(name="غیرفعال")

        for name in ["پشتو", "دری", "انګلیسی", "اردو", "ازبکی"]:
            Language.objects.get_or_create(name=name)

        for name in ["لیسانس", "ماستر", "دیپلم", "دکترا"]:
            Degree.objects.get_or_create(name=name)

        for name in ["کشاورز", "معلم", "راننده", "مهندس", "تجارت", "دکتر", "دولت", "متفرقه"]:
            Job.objects.get_or_create(name=name)

        for name in ["کابل", "کندهار", "هرات", "مزارشریف", "بلخ", "ننگرهار"]:
            Province.objects.get_or_create(name=name)

        province_map = {
            province.name: province for province in Province.objects.all()}
        district_names = {
            "کابل": ["پغمان", "ده‌سبز", "چاراسیا", "خیربخا"],
            "کندهار": ["ارغنداب", "ژری", "دامن", "شاه‌ولی‌کوت"],
            "هرات": ["گوزران", "کوشک", "پشتون‌زرغون", "انجیل"],
            "مزارشریف": ["نهرین", "دولت‌آباد", "بلخ", "شولګر"],
            "بلخ": ["چهاربولک", "ده‌دادی", "شهرک", "مزار"],
            "ننگرهار": ["جلال‌آباد", "بهسود", "سرخ‌رود", "هساره"],
        }
        for province_name, districts in district_names.items():
            province = province_map[province_name]
            for district_name in districts:
                District.objects.get_or_create(
                    province=province, name=district_name)

        for name in ["آزمون", "میان ترم", "فینال", "تکلیف"]:
            ExamType.objects.get_or_create(name=name)

        for name in ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله", "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]:
            Month.objects.get_or_create(name=name)

        academic_year, _ = AcademiceYear.objects.get_or_create(
            year=1404,
            defaults={
                "start_date": date(2025, 3, 21),
                "end_date": date(2026, 3, 20),
            },
        )

        subjects = [
            "ریاضی",
            "علوم",
            "دین و اخلاق",
            "پشتو",
            "دری",
            "انګلیسی",
            "کامپیوتر",
            "علوم اجتماعی",
        ]
        for name in subjects:
            Subject.objects.get_or_create(name=name)

        teacher_names = [
            ("احمد", "رحیمی", "ریاضی"),
            ("نادیا", "کریمی", "علوم"),
            ("فرید", "احمدی", "فزیک"),
            ("سحر", "نیازی", "انگلیسی"),
            ("جمال", "صفی", "کامپیوتر"),
            ("امینه", "حسینی", "بیولوژی"),
            ("حسن", "ظفری", "تاریخ"),
            ("زینب", "منصور", "شیمی"),
        ]

        degrees = list(Degree.objects.all())
        jobs = list(Job.objects.all())
        teachers = []
        for index, (first_name, last_name, major) in enumerate(teacher_names, start=1):
            teacher, _ = Teacher.objects.get_or_create(
                name=first_name,
                fname="",
                last_name=last_name,
                phone=f"07{(index * 12345) % 10000000:08d}",
                major=major,
                degree=degrees[index % len(degrees)],
                job=jobs[index % len(jobs)],
                years_of_service=3 + index,
                registered_date=date(2019 + (index % 4), 1, 10),
                graduation_year=1395 + index,
                salary=6000 + index * 350,
                tax=150 + index * 20,
                status=status_active,
            )
            teachers.append(teacher)

        classes = []
        for grade in range(1, 7):
            for section in ["الف", "ب", "ج"]:
                class_obj, _ = Classes.objects.get_or_create(
                    grade=grade,
                    alpha_grade=f"{grade}-{section}",
                    section=section,
                    academice_year=academic_year,
                    defaults={
                        "guidence": teachers[(grade + len(section)) % len(teachers)],
                        "capacity": 35,
                        "start_time": "08:00:00",
                        "end_time": "15:00:00",
                        "turn": "صبح",
                        "status": status_active,
                    },
                )
                classes.append(class_obj)

        for class_obj in classes:
            for index, subject_name in enumerate(subjects[:4]):
                subject = Subject.objects.get(name=subject_name)
                TeacherSubject.objects.get_or_create(
                    teacher=teachers[(class_obj.id + index) % len(teachers)],
                    subject=subject,
                    classs=class_obj,
                    academice_year=academic_year,
                )

        first_names = [
            "احمد", "علی", "حسن", "هادی", "نور", "ذکی", "موسی", "سمیم", "رحمان", "امید",
            "عایشه", "مریم", "سحر", "نبلا", "مینا", "سارا", "لیلا", "نازیه", "حوا", "آیه",
            "کریم", "فرید", "یاسین", "ویس", "سلیم", "نعیم", "احسان", "کامران", "حمید", "رفیع",
            "خالد", "طارق", "عمران", "عثمان", "بلال", "عدنان", "عارف", "وحید", "انور", "عزیز",
            "حفصه", "مریمه", "فوزیه", "شبنم", "شکریه", "سمیرا", "لیلا", "صنعا", "روما", "گل‌آلاء",
        ]
        last_names = [
            "احمدی", "رحیمی", "نیازی", "صفی", "کریمی", "حسینی", "ظفری", "منصور", "قادیری", "خان",
            "یوسفی", "وردک", "مجددی", "اکبری", "گل", "جان", "امین", "صدیقی", "زدران", "حاشمی",
        ]

        student_counter = 1
        while student_counter <= count:
            for class_obj in classes:
                if student_counter > count:
                    break

                first_name = first_names[(
                    student_counter - 1) % len(first_names)]
                father_name = last_names[(
                    student_counter + 2) % len(last_names)]
                grand_father_name = last_names[(
                    student_counter + 5) % len(last_names)]
                province = Province.objects.order_by("id")[
                    (student_counter - 1) % Province.objects.count()
                ]
                district = District.objects.filter(
                    province=province).order_by("id").first()
                if district is None:
                    district = District.objects.order_by("id").first()

                student, _ = Student.objects.get_or_create(
                    school_id=1000 + student_counter,
                    defaults={
                        "name": first_name,
                        "fname": father_name,
                        "gfname": grand_father_name,
                        "card_id": f"کارت-{100000 + student_counter}",
                        "birth_date": date(2012 + (student_counter % 5), (student_counter % 12) + 1, (student_counter % 27) + 1),
                        "mother_language": Language.objects.order_by("id").first(),
                        "nationality": "افغان",
                        "father_job": Job.objects.order_by("id").first(),
                        "original_province": province,
                        "original_district": district,
                        "original_zone": 1 + (student_counter % 8),
                        "original_village": f"روستا {student_counter}",
                        "now_province": province,
                        "now_district": district,
                        "now_zone": 1 + (student_counter % 6),
                        "now_village": f"روستا {student_counter}",
                        "registered_date": date(2024, 3, 10),
                        "detached_date": None,
                        "phone": f"079{(student_counter * 76543) % 10000000:07d}",
                        "status": status_active,
                    },
                )

                StudentClass.objects.get_or_create(
                    student=student,
                    classs=class_obj,
                    academice_year=academic_year,
                )

                for month in Month.objects.all()[:3]:
                    Attendance.objects.get_or_create(
                        student=student,
                        classs=class_obj,
                        month=month,
                        academice_year=academic_year,
                        defaults={
                            "present": 18 + (student_counter % 10),
                            "present_percent": 70 + (student_counter % 25),
                            "absent": 2 + (student_counter % 5),
                            "sick": 1 + (student_counter % 3),
                            "excused": 1 + (student_counter % 4),
                            "alldays": 25,
                        },
                    )

                for subject in Subject.objects.all()[:3]:
                    teacher = teachers[(
                        student_counter + class_obj.id) % len(teachers)]
                    Assessment.objects.get_or_create(
                        student=student,
                        teacher=teacher,
                        subject=subject,
                        classs=class_obj,
                        month=Month.objects.order_by("id").first(),
                        academice_year=academic_year,
                        defaults={
                            "score": 60 + (student_counter % 40),
                            "max_score": 100,
                        },
                    )

                student_counter += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully recreated the database with {count} Persian/Afghan student records."
            )
        )
