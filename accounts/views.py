from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse

useradmin = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "teacher_profile") and request.user.teacher_profile and not request.user.is_staff:
            return redirect(reverse("teachers:dashboard"))
        return redirect(reverse("dashboard:admin-dashboard"))

    error = ""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        password = (request.POST.get("password") or "").strip()
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user=user)
            # Auto-detect role: Teacher vs Admin
            if hasattr(user, "teacher_profile") and user.teacher_profile and not user.is_staff:
                return redirect(reverse("teachers:dashboard"))
            return redirect(reverse("dashboard:admin-dashboard"))
        else:
            error = "ایمیل یا رمز عبور اشتباه است!"

    return render(request, "accounts/login.html", {"error": error})


def custom_logout(request):
    logout(request)
    return redirect(reverse("accounts:login"))
