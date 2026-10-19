import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from dashboard.models import Student, Classes, StudentClass, AcademiceYear, Month, Fee, Expense

def seed():
    print("Starting Finance Data Seeding...")
    year1403 = AcademiceYear.objects.filter(year=1403).first()
    if not year1403:
        year1403 = AcademiceYear.objects.first()

    months = list(Month.objects.all().order_by("id"))
    students = list(Student.objects.filter(status__id=1))
    student_classes = {sc.student_id: sc.classs for sc in StudentClass.objects.select_related("classs").all()}

    print(f"Found {len(students)} active students and {len(months)} months.")

    # 1. Update existing fees
    existing_fees = Fee.objects.all()
    for idx, f in enumerate(existing_fees, 1):
        if not f.receipt_number:
            f.receipt_number = f"REC-1403-{1000 + idx}"
        if not f.fee_category:
            f.fee_category = "شهریه ماهوار"
        if not f.payment_method:
            f.payment_method = "نقدی (صندوق مکتب)"
        f.save()
    print(f"Updated {existing_fees.count()} existing fee records.")

    # 2. Add realistic fees for students across months
    # Target ~35-40 realistic fee records
    categories = ["شهریه ماهوار", "شهریه ماهوار", "شهریه ماهوار", "فیس داخله", "ترانسپورت", "کتاب و قرطاسیه"]
    methods = ["نقدی (صندوق مکتب)", "نقدی (صندوق مکتب)", "واریز به حساب بانکی", "حواله صرافی"]
    
    current_fee_count = Fee.objects.count()
    start_rec_num = 1000 + current_fee_count + 1

    sample_months = months[:6]  # Hamal, Sawr, Jawza, Saratan, Asad, Sonbola
    month_dates = [
        datetime.date(2024, 4, 15),
        datetime.date(2024, 5, 18),
        datetime.date(2024, 6, 20),
        datetime.date(2024, 7, 22),
        datetime.date(2024, 8, 25),
        datetime.date(2024, 9, 28),
    ]

    new_fees = []
    for s_idx, student in enumerate(students[:20]):
        cls = student_classes.get(student.id)
        # 1-3 payments per student
        for m_idx in range(s_idx % 3 + 1):
            m = sample_months[m_idx]
            p_date = month_dates[m_idx]
            amount = 4500
            
            # create full, partial, or small balance
            mod = (s_idx + m_idx) % 5
            if mod == 0:
                paied = 4500  # full
            elif mod == 1:
                paied = 3000  # partial
            elif mod == 2:
                paied = 4500  # full
            elif mod == 3:
                paied = 2500  # partial
            else:
                paied = 4500  # full

            rec_num = f"REC-1403-{start_rec_num}"
            start_rec_num += 1

            cat = categories[(s_idx + m_idx) % len(categories)]
            pm = methods[(s_idx + m_idx) % len(methods)]
            note = "تسویه گردید" if paied == amount else "مانده قسط هفته آینده پرداخت می‌شود"

            # Check if fee already exists for this student, month, year
            if not Fee.objects.filter(student=student, month=m, academice_year=year1403).exists():
                fee = Fee(
                    student=student,
                    class_section=cls,
                    month=m,
                    amount=amount,
                    paied=paied,
                    payment_date=p_date,
                    academice_year=year1403,
                    receipt_number=rec_num,
                    payment_method=pm,
                    fee_category=cat,
                    notes=note,
                )
                new_fees.append(fee)

    if new_fees:
        Fee.objects.bulk_create(new_fees)
        print(f"Successfully created {len(new_fees)} new fee payments.")

    # 3. Add realistic Expenses
    sample_expenses = [
        # Salaries
        ("معاشات استادان و پرسونل", "معاش برج حمل کادر تدریسی و اداری مکتب", 145000, datetime.date(2024, 4, 30), "استادان و پرسونل اداری", "EXP-1403-501", "واریز به حساب بانکی", 2),
        ("معاشات استادان و پرسونل", "معاش برج ثور استادان و پرسونل", 145000, datetime.date(2024, 5, 30), "استادان و پرسونل اداری", "EXP-1403-502", "واریز به حساب بانکی", 3),
        ("معاشات استادان و پرسونل", "معاش برج جوزا استادان و پرسونل", 148000, datetime.date(2024, 6, 30), "استادان و پرسونل اداری", "EXP-1403-503", "واریز به حساب بانکی", 1),
        ("معاشات استادان و پرسونل", "معاش برج سرطان استادان و کادر خدماتی", 145000, datetime.date(2024, 7, 30), "استادان و پرسونل اداری", "EXP-1403-504", "واریز به حساب بانکی", 4),
        ("معاشات استادان و پرسونل", "معاش برج اسد استادان و پرسونل", 146500, datetime.date(2024, 8, 30), "استادان و پرسونل اداری", "EXP-1403-505", "واریز به حساب بانکی", 5),
        
        # Rent
        ("کرایه تعمیر مکتب", "کرایه تعمیر مکتب - سه ماهه اول سال تعلیمی ۱۴۰۳", 120000, datetime.date(2024, 4, 5), "حاجی محمدرضا (مالک ساختمان)", "EXP-1403-506", "حواله بانکی", 2),
        ("کرایه تعمیر مکتب", "کرایه تعمیر مکتب - سه ماهه دوم سال تعلیمی ۱۴۰۳", 120000, datetime.date(2024, 7, 5), "حاجی محمدرضا (مالک ساختمان)", "EXP-1403-507", "حواله بانکی", 4),
        
        # Utilities & Internet
        ("برق، آب و انترنت", "بل صرفیه برق مکتب - دوره بهار", 14500, datetime.date(2024, 5, 12), "شرکت برشنا", "EXP-1403-508", "نقدی (بانک)", 3),
        ("برق، آب و انترنت", "اشتراک انترنت پرسرعت فایبرنوری - شش ماهه", 18000, datetime.date(2024, 4, 10), "شرکت مخابراتی افغان بیسیم", "EXP-1403-509", "نقدی", 2),
        ("برق، آب و انترنت", "بل صرفیه برق و آب مکتب - دوره تابستان", 16800, datetime.date(2024, 8, 14), "شرکت برشنا", "EXP-1403-510", "نقدی", 5),

        # Stationery & Books
        ("قرطاسیه، چاپ و مواد درسی", "چاپ اوراق امتحانات چهارونیم ماهه، شقه نمرات و دفتر حاضری", 24500, datetime.date(2024, 6, 15), "مطبعه کابل پرس", "EXP-1403-511", "نقدی", 1),
        ("قرطاسیه، چاپ و مواد درسی", "خرید ماژیک، تخته‌پاک و ملزومات صنوف درسی", 8500, datetime.date(2024, 4, 8), "قرطاسیه‌فروشی دانش", "EXP-1403-512", "نقدی", 2),
        ("قرطاسیه، چاپ و مواد درسی", "خرید اوراق رسمی و اطلاع‌نامه‌های شاگردان", 12000, datetime.date(2024, 7, 18), "مطبعه شرق", "EXP-1403-513", "نقدی", 4),

        # Maintenance & Furniture
        ("تعمیرات، حفظ و مراقبت", "ترمیم میز و چوکی‌های صنوف و جوشکاری دروازه‌ها", 15000, datetime.date(2024, 5, 20), "کارگاه فلزکاری برادران رحیمی", "EXP-1403-514", "نقدی", 3),
        ("تعمیرات، حفظ و مراقبت", "رنگ‌مالی صنوف ابتدایی و دهلیزهای مکتب", 28000, datetime.date(2024, 8, 10), "استاد ظاهر نقاش", "EXP-1403-515", "نقدی", 5),

        # Tech Equipment
        ("تجهیزات و فناوری", "خرید یک پایه پرینتر چندکاره برای شعبه اداری و امتحانات", 22500, datetime.date(2024, 4, 25), "فروشگاه کامپیوتر آریا", "EXP-1403-516", "نقدی", 2),
    ]

    new_expenses = []
    for cat, title, amt, p_date, recip, r_num, pm, m_id in sample_expenses:
        if not Expense.objects.filter(receipt_number=r_num).exists():
            month_obj = Month.objects.filter(id=m_id).first()
            exp = Expense(
                category=cat,
                title=title,
                amount=amt,
                payment_date=p_date,
                recipient=recip,
                receipt_number=r_num,
                payment_method=pm,
                academice_year=year1403,
                month=month_obj,
                notes="تأیید شده توسط مدیریت مالی و آمریت مکتب",
            )
            new_expenses.append(exp)

    if new_expenses:
        Expense.objects.bulk_create(new_expenses)
        print(f"Successfully created {len(new_expenses)} school expenses.")

    total_f = Fee.objects.count()
    total_e = Expense.objects.count()
    print(f"Total Fees in DB: {total_f}")
    print(f"Total Expenses in DB: {total_e}")
    print("Finance seeding complete!")

if __name__ == "__main__":
    seed()
