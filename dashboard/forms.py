from django import forms
from .models import Student, Subject, Classes


class StudentForm(forms.Form):
    school_id = forms.IntegerField(required=True)
    class_section = forms.CharField(max_length=20)
    name = forms.CharField(max_length=50, required=True)
    fname = forms.CharField(max_length=50, required=True)
    gfname = forms.CharField(max_length=50, required=True)
    card_id = forms.CharField(max_length=50, required=True)
    birth_date = forms.DateField(required=True)
    mother_language = forms.IntegerField(required=True)
    nationality = forms.CharField(max_length=50, required=True)
    father_job = forms.CharField(max_length=100, required=True)
    original_province = forms.IntegerField(required=True)
    original_district = forms.IntegerField(required=True)
    original_zone = forms.IntegerField(required=True)
    original_village = forms.CharField(max_length=50, required=True)
    now_province = forms.IntegerField(required=True)
    now_district = forms.IntegerField(required=True)
    now_zone = forms.IntegerField(required=True)
    now_village = forms.CharField(max_length=50, required=True)
    registered_date = forms.DateField(required=True)
    detached_date = forms.DateField(required=False)
    phone = forms.CharField(max_length=15, required=True)
    status = forms.IntegerField(required=True)
    class_section = forms.CharField(max_length=20, required=True)
    academice_year = forms.IntegerField(required=True)


class TeacherForm(forms.Form):
    id = forms.IntegerField(required=False)
    name = forms.CharField(max_length=50, required=True)
    fname = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=20, required=True)
    major = forms.CharField(max_length=50, required=True)
    degree = forms.CharField(max_length=50, required=True)
    job = forms.CharField(max_length=20, required=True)
    years_of_service = forms.IntegerField(required=True)
    registered_date = forms.DateField(required=True)
    detached_date = forms.DateField(required=False)
    graduation_year = forms.IntegerField(required=True)
    salary = forms.IntegerField(required=True)
    tax = forms.IntegerField(required=True)
    status = forms.IntegerField(required=True)
    guidence_at = forms.CharField(required=False)


class ClassForm(forms.Form):
    academice_year = forms.IntegerField(required=True)
    grade = forms.CharField(max_length=20, required=True)
    section = forms.CharField(max_length=10, required=True)
    guidence = forms.IntegerField(required=False)
    start_time_hour = forms.IntegerField(required=True)
    start_time_minute = forms.IntegerField(required=True)
    end_time_hour = forms.IntegerField(required=True)
    end_time_minute = forms.IntegerField(required=True)
    capacity = forms.IntegerField(required=True)


class SubjectForm(forms.ModelForm):
    """
    Academic Curriculum Subject Form (فرم ایجاد و ویرایش مضامین درسی)
    """
    class Meta:
        model = Subject
        fields = [
            "name",
            "code",
            "category",
            "educational_level",
            "weekly_hours",
            "passing_score",
            "total_score",
            "is_active",
            "description",
            "classes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "input-control font-bold",
                "placeholder": "مثلاً: فزیک، ریاضیات عالی، تفسیر شریف...",
                "required": "required",
            }),
            "code": forms.TextInput(attrs={
                "class": "input-control",
                "placeholder": "مثلاً: PHY-108, QUR-101",
            }),
            "category": forms.Select(attrs={
                "class": "input-control font-bold",
            }),
            "educational_level": forms.Select(attrs={
                "class": "input-control font-bold",
            }),
            "weekly_hours": forms.NumberInput(attrs={
                "class": "input-control font-bold",
                "min": "1",
                "max": "12",
            }),
            "passing_score": forms.NumberInput(attrs={
                "class": "input-control font-bold",
                "min": "0",
                "max": "100",
                "step": "0.5",
            }),
            "total_score": forms.NumberInput(attrs={
                "class": "input-control font-bold",
                "min": "10",
                "max": "100",
                "step": "0.5",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "custom-checkbox",
            }),
            "description": forms.Textarea(attrs={
                "class": "input-control",
                "rows": "3",
                "placeholder": "توضیحات و اهداف آموزشی مضمون بر اساس لوایح معارف...",
            }),
            "classes": forms.CheckboxSelectMultiple(attrs={
                "class": "classes-checkbox-grid",
            }),
        }
