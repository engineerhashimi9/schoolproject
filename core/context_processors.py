"""
Global Context Processors for School System
Supplies academic dates, active year, and user role metadata to all templates.
"""

from .utils import get_current_jalali_date_str, get_active_academic_year


def global_academic_context(request):
    """
    Makes academic context available globally across all templates without manual injection.
    """
    user = getattr(request, "user", None)
    is_auth = user and user.is_authenticated

    is_teacher = False
    current_teacher = None
    if is_auth:
        if hasattr(user, "teacher_profile") and user.teacher_profile:
            is_teacher = True
            current_teacher = user.teacher_profile

    is_school_admin = bool(is_auth and (user.is_staff or user.is_superuser))

    return {
        "jalali_date_str": get_current_jalali_date_str(),
        "active_academic_year": get_active_academic_year(),
        "is_teacher": is_teacher,
        "is_school_admin": is_school_admin,
        "current_teacher": current_teacher,
    }
