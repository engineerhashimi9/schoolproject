from django.shortcuts import render
from django.contrib.auth import authenticate,login
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
useradmin=get_user_model()
# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("dashboard:admin-dashboard"))

    error = ""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = (request.POST.get("password") or "").strip()
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user=user)
            return redirect(reverse("dashboard:admin-dashboard"))
        else:
            error = "ایمیل یا رمز عبور اشتباه است!"

    return render(request, "accounts/login.html", {"error": error})

def custom_logout(request):
    logout(request)
    return redirect(reverse("accounts:login"))