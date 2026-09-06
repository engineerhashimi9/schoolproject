from django import forms
from . models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "id", "name", "fname", "gfname", "card_id", "birth_date", "mother_language", "nationality", "father_job", "original_province", "original_district",
            "original_zone", "original_village", "now_province", "now_district", "now_zone", "now_village", "registered_date", "detached_date", "phone", "status",
        ]
