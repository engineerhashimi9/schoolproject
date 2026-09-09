from django import forms
from . models import Student


class StudentForm(forms.Form):
    id = forms.IntegerField(required=True)
    class_section = forms.CharField(max_length=20)
    name = forms.CharField(max_length=50, required=True)
    fname = forms.CharField(max_length=50, required=True)
    gfname = forms.CharField(max_length=50, required=True)
    card_id = forms.CharField(max_length=50, required=True)
    birth_date = forms.DateField(required=True)
    mother_language = forms.IntegerField(required=True)
    nationality = forms.CharField(max_length=50, required=True)
    father_job=forms.CharField( max_length=100, required=True)
    original_province = forms.IntegerField(required=True)
    original_district = forms.IntegerField(required=True)
    original_zone = forms.IntegerField(required=True)
    original_village = forms.CharField(max_length=50, required=True)
    now_province = forms.IntegerField(required=True)
    now_district = forms.IntegerField(required=True)
    now_zone = forms.IntegerField(required=True)
    now_village = forms.CharField(max_length=50, required=True)
    registered_date = forms.DateField(required=True)
    detached_date = forms.DateField(required=True)
    phone = forms.CharField(max_length=13, required=True)
    status = forms.IntegerField(required=True)
    class_section=forms.CharField( max_length=20, required=True)
