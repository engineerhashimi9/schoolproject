import os

models_path = os.path.join("dashboard", "models.py")

with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    classes = models.ManyToManyField('Classes', blank=True, related_name="subjects")

    def __str__(self) -> str:
        return f"{self.name}\""""

replacement = """class Subject(models.Model):
    \"\"\"
    Academic Curriculum Subject (مضمون درسی نصاب تعلیمی معارف افغانستان)
    Flexible to accommodate Afghan Ministry of Education requirements:
    - Primary (ابتدائیه): Grades 1-6
    - Middle (متوسطه): Grades 7-9
    - High School / Lycée (لیسه): Grades 10-12
    - Standard categories: علوم دینی، زبان و ادبیات، ساینس، ریاضیات، علوم اجتماعی، فناوری، تربیت بدنی
    \"\"\"
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
        return cat_map.get(self.category, "badge-default")"""

normalized_content = content.replace("\r\n", "\n")
if target in normalized_content:
    new_content = normalized_content.replace(target, replacement)
    with open(models_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: Subject model updated.")
else:
    print("ERROR: Target not found.")
