with open("dashboard/views.py", "r", encoding="utf-8") as f:
    c = f.read()

target = """def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            return redirect(reverse("accounts:login"))

    return wrapper"""

replacement = """def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        if hasattr(request.user, "teacher_profile") and request.user.teacher_profile:
            return redirect(reverse("teachers:dashboard"))
        return redirect(reverse("accounts:login"))

    return wrapper"""

if target in c:
    c = c.replace(target, replacement, 1)
    with open("dashboard/views.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("SUCCESS: Updated is_admin in dashboard/views.py")
else:
    target_crlf = target.replace("\n", "\r\n")
    replacement_crlf = replacement.replace("\n", "\r\n")
    if target_crlf in c:
        c = c.replace(target_crlf, replacement_crlf, 1)
        with open("dashboard/views.py", "w", encoding="utf-8") as f:
            f.write(c)
        print("SUCCESS: Updated is_admin in dashboard/views.py (CRLF)")
    else:
        print("Target not found")
