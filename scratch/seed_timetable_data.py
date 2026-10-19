import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from dashboard.models import Classes, Teacher, Subject, AcademiceYear, TimeTable

def seed():
    print("=== SEEDING AUTHENTIC AFGHAN TIMETABLE DATA ===")

    year1403 = AcademiceYear.objects.filter(year=1403).first() or AcademiceYear.objects.first()
    print(f"Academic Year: {year1403.year}")

    # Classes to seed
    classes = list(Classes.objects.all().order_by("grade", "section"))
    teachers = list(Teacher.objects.filter(status__id=1))
    subjects = list(Subject.objects.all())

    if not classes or not teachers or not subjects:
        print("Missing classes, teachers, or subjects!")
        return

    print(f"Available: {len(classes)} classes, {len(teachers)} teachers, {len(subjects)} subjects.")

    # Clean existing slots for year 1403 to build an immaculate, conflict-free schedule
    TimeTable.objects.filter(academic_year=year1403).delete()
    print("Cleared old timetable slots for Year 1403.")

    # Standard distribution for Class 10-A (دهم الف) and others
    # 6 Days x 6 Periods = 36 periods per class
    # Subject schedule mapping for typical Afghan high school:
    # 1: Quran/Dinyat (3 periods)
    # 2: Dari (4 periods)
    # 3: Pashto (3 periods)
    # 4: Math/Geometry (6 periods)
    # 5: Physics (4 periods)
    # 6: Chemistry (3 periods)
    # 7: Biology (3 periods)
    # 8: English (3 periods)
    # 9: History/Geography (3 periods)
    # 10: Computer (2 periods)
    # 11: PE / Art (2 periods)

    # Let's assign specialized teachers to subjects
    teacher_sub_map = {}
    for idx, sub in enumerate(subjects):
        t = teachers[idx % len(teachers)]
        teacher_sub_map[sub.id] = t

    # Helper: build a schedule for a class without conflict
    # Used slots by teacher: (teacher_id, day, period) -> True
    used_teacher_slots = set()

    seeded_slots = []
    # Seed Class 10-A first, plus other classes
    c10a = Classes.objects.filter(alpha_grade="دهم", section="الف").first()
    other_cls = [c for c in classes if c != c10a]
    target_classes = ([c10a] if c10a else []) + other_cls[:5]

    for c_idx, cls in enumerate(target_classes):
        cls_subjects = list(cls.subjects.all())
        if not cls_subjects:
            cls_subjects = subjects

        sub_index = 0
        for day in range(1, 7): # شنبه (1) تا پنج‌شنبه (6)
            for period in range(1, 7): # ساعت اول (1) تا ساعت ششم (6)
                # Pick a subject and a teacher who is NOT busy at this day & period
                assigned = False
                for attempt in range(len(cls_subjects)):
                    candidate_sub = cls_subjects[(sub_index + attempt) % len(cls_subjects)]
                    # find a suitable teacher for this candidate_sub
                    candidate_teachers = [t for t in teachers if (t.id, day, period) not in used_teacher_slots]
                    if candidate_teachers:
                        # pick preferred or first free teacher
                        pref_t = teacher_sub_map.get(candidate_sub.id)
                        t = pref_t if pref_t in candidate_teachers else candidate_teachers[0]
                        
                        used_teacher_slots.add((t.id, day, period))
                        room_name = f"اتاق {cls.alpha_grade} {cls.section}"
                        
                        slot = TimeTable(
                            classs=cls,
                            teacher=t,
                            subject=candidate_sub,
                            academic_year=year1403,
                            day_of_week=day,
                            period=period,
                            room_number=room_name,
                            notes="ساعت درسی رسمی مکتب",
                        )
                        seeded_slots.append(slot)
                        sub_index = (sub_index + attempt + 1) % len(cls_subjects)
                        assigned = True
                        break
                
                if not assigned:
                    # If all teachers busy, leave empty
                    pass

    TimeTable.objects.bulk_create(seeded_slots)
    print(f"✓ Successfully seeded {len(seeded_slots)} timetable slots across {len(target_classes)} classes!")
    print(f"Total TimeTable records in DB: {TimeTable.objects.count()}")

if __name__ == "__main__":
    seed()
