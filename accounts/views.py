from django.shortcuts import render
from django.contrib.auth import authenticate,login
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
useradmin=get_user_model()
# Create your views here.
def login_view(request):
    error=""
    if request.method=="POST" :
        email=request.POST.get("email")
        password=request.POST.get("password")
        user=authenticate(email=email,password=password)
        if user is not None :
            login(request,user=user)
            return redirect(reverse("dashboard:admin-dashboard"))
        else :
            error="ایمیل یا رمز عبور اشتباه!"
            
    return render(request, "accounts/login.html",{"error":error})