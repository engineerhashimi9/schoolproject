import os
import sys
import django

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from dashboard.models import Subject, Classes

def enrich_subjects():
    metadata = {
        "قرآن کریم و تجوید": {
            "code": "QUR-101",
            "category": "علوم دینی و اسلامی",
            "educational_level": "عمومی",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "آموزش روخوانی، روان‌خوانی، حفظ، تجوید و احکام تلاوت کلام‌الله مجید."
        },
        "تعلیمات دینی و تفسیر": {
            "code": "ISL-102",
            "category": "علوم دینی و اسلامی",
            "educational_level": "عمومی",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "عقاید اسلامی، فقه، سیرت نبوی، احکام شرعی و مفاهیم تفسیر آیات."
        },
        "ادبیات و قرائت دری": {
            "code": "DAR-103",
            "category": "زبان و ادبیات",
            "educational_level": "عمومی",
            "weekly_hours": 4,
            "passing_score": 40.0,
            "description": "آموزش قواعد زبان دری، صرف و نحو، املا، انشا، متون کهن و نظم و نثر معاصر."
        },
        "زبان و ادبیات پشتو": {
            "code": "PAS-104",
            "category": "زبان و ادبیات",
            "educational_level": "عمومی",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "دستور زبان پشتو، گرامر، متون ادبی، انشا، لغات و قرائت زبان رسمی کشور."
        },
        "لسان انگلیسی": {
            "code": "ENG-105",
            "category": "زبان و ادبیات",
            "educational_level": "متوسطه",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "مهارت‌های چهارگانه زبان انگلیسی (Reading, Writing, Listening, Speaking) و گرامر."
        },
        "ریاضیات عالی": {
            "code": "MTH-106",
            "category": "ریاضیات و هندسه",
            "educational_level": "لیسه",
            "weekly_hours": 4,
            "passing_score": 40.0,
            "description": "مباحث جبر، معادلات، تابع، لیمیت، مشتق، انتگرال و تحلیل ریاضیات عالی."
        },
        "هندسه و مثلثات": {
            "code": "GEO-107",
            "category": "ریاضیات و هندسه",
            "educational_level": "لیسه",
            "weekly_hours": 2,
            "passing_score": 40.0,
            "description": "هندسه تحلیلی، فضایی، روابط مثلثاتی، دایره و احجام فضایی."
        },
        "فزیک": {
            "code": "PHY-108",
            "category": "علوم ساینسی و طبیعی",
            "educational_level": "لیسه",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "میکانیک، حرکت، انرژی، نور، الکتریسیته، مغناطیس و مباحث فزیک مدرن معارف."
        },
        "کیمیا": {
            "code": "CHM-109",
            "category": "علوم ساینسی و طبیعی",
            "educational_level": "لیسه",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "کیمیای عمومی، غیرعضوی، عضوی، جدول دورانی عناصر و ترکیبات کیمیاوی."
        },
        "بیولوژی": {
            "code": "BIO-110",
            "category": "علوم ساینسی و طبیعی",
            "educational_level": "لیسه",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "علوم حیات، اناتومی، فزیولوژی، ژنتیک، نباتات، حیوانات و محیط زیست."
        },
        "تاریخ معاصر افغانستان": {
            "code": "HIS-111",
            "category": "علوم اجتماعی و بشری",
            "educational_level": "عمومی",
            "weekly_hours": 2,
            "passing_score": 40.0,
            "description": "تاریخ قدیم، قرون وسطی و معاصر افغانستان، قیام‌ها، استقلال و شخصیت‌های ملی."
        },
        "جغرافیه عمومی": {
            "code": "GEOG-112",
            "category": "علوم اجتماعی و بشری",
            "educational_level": "عمومی",
            "weekly_hours": 2,
            "passing_score": 40.0,
            "description": "جغرافیای طبیعی، اقتصادی، ولایات افغانستان، اقلیم، ناهمواری‌ها و جغرافیای جهان."
        },
        "کمپیوتر و فناوری معلومات": {
            "code": "CMP-113",
            "category": "فناوری، مهارت و هنر",
            "educational_level": "عمومی",
            "weekly_hours": 2,
            "passing_score": 40.0,
            "description": "مفاهیم اساسی IT، ویندوز، بسته‌های آفیس (Word, Excel)، اینترنت و امنیت دیجیتال."
        },
        "تعلیم و تربیه بدنی": {
            "code": "SPT-114",
            "category": "تربیت بدنی و صحت",
            "educational_level": "عمومی",
            "weekly_hours": 1,
            "passing_score": 40.0,
            "description": "ورزش، تمرینات آمادگی جسمانی، صحت و حفظ‌الصحه فردی و بازی‌های گروهی."
        },
        "حسن خط و رسم": {
            "code": "ART-115",
            "category": "فناوری، مهارت و هنر",
            "educational_level": "ابتدائیه",
            "weekly_hours": 2,
            "passing_score": 40.0,
            "description": "تعلیم خط نستعلیق و نسخ، اصول نقاشی، رنگ‌آمیزی و زیبایی‌شناسی اسلامی."
        },
        # Standard Primary/Middle Subjects
        "ساینس و محیط زیست": {
            "code": "SCI-116",
            "category": "علوم ساینسی و طبیعی",
            "educational_level": "ابتدائیه",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "مفاهیم ابتدایی علوم تجربی، موجودات زنده، ماده و محیط زیست برای صنوف ابتدائیه."
        },
        "تهذیب و اخلاق اسلامی": {
            "code": "THZ-117",
            "category": "علوم دینی و اسلامی",
            "educational_level": "ابتدائیه",
            "weekly_hours": 2,
            "passing_score": 40.0,
            "description": "تربیت اخلاقی، آداب اسلامی، احترام به والدین و اساتید و مسئولیت‌های اجتماعی."
        },
        "ریاضیات دوره ابتدائیه": {
            "code": "MTH-118",
            "category": "ریاضیات و هندسه",
            "educational_level": "ابتدائیه",
            "weekly_hours": 4,
            "passing_score": 40.0,
            "description": "چهار عمل اصلی حساب، کسرها، مقیاس‌ها و اشکال هندسی ساده برای صنوف پایه."
        },
        "عقاید و فقه": {
            "code": "FIQ-119",
            "category": "علوم دینی و اسلامی",
            "educational_level": "متوسطه",
            "weekly_hours": 3,
            "passing_score": 40.0,
            "description": "عقاید اسلامی و مسائل فقهی (عبادات، معاملات، طهارت، نماز، روزه و احکام)."
        },
    }

    for name, data in metadata.items():
        subj, created = Subject.objects.get_or_create(name=name)
        subj.code = data["code"]
        subj.category = data["category"]
        subj.educational_level = data["educational_level"]
        subj.weekly_hours = data["weekly_hours"]
        subj.passing_score = data["passing_score"]
        subj.description = data["description"]
        subj.is_active = True
        subj.save()
        status = "Created" if created else "Updated"
        print(f"[{status}] {subj.name} ({subj.code}) - {subj.category} ({subj.educational_level})")

    # Ensure all classes have appropriate subjects assigned
    all_subjects = list(Subject.objects.filter(is_active=True))
    for c in Classes.objects.all():
        if c.subjects.count() == 0:
            c.subjects.set(all_subjects)

    print(f"\nTotal Subjects in Database: {Subject.objects.count()}")

if __name__ == "__main__":
    enrich_subjects()
