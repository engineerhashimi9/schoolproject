import re

base_path = "dashboard/templates/dashboard/base.html"

with open(base_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Teacher Portal to sidebar nav
target_menu = """            <li class="{% if 'worker' in request.resolver_match.url_name %}active{% endif %}">
              <a href="{% url 'dashboard:worker-list' %}">
                <i class="fa-solid fa-users"></i> کارمندان و اساتید
              </a>
            </li>"""

replacement_menu = """            <li class="{% if 'teacher-' in request.resolver_match.url_name %}active{% endif %}">
              <a href="{% url 'dashboard:teacher-portal' %}">
                <i class="fa-solid fa-chalkboard-user"></i> پورتال اساتید
              </a>
            </li>
            <li class="{% if 'worker' in request.resolver_match.url_name %}active{% endif %}">
              <a href="{% url 'dashboard:worker-list' %}">
                <i class="fa-solid fa-users"></i> کارمندان و اساتید
              </a>
            </li>"""

# 2. Update user-card in sidebar footer
old_user_card = """            <div class="user-info">
              <i class="fa-solid fa-user-circle"></i>
              <span>{% if request.user.name %}{{ request.user.name }} {{ request.user.last_name }}{% else %}مدیر سیستم{% endif %}</span>
            </div>
            <span class="badge">مدیریت</span>"""

new_user_card = """            <div class="user-info">
              <i class="fa-solid fa-user-circle"></i>
              <span>
                {% if request.user.teacher_profile %}
                  استاد {{ request.user.teacher_profile.name }}
                {% elif request.user.name %}
                  {{ request.user.name }} {{ request.user.last_name }}
                {% else %}
                  مدیر سیستم
                {% endif %}
              </span>
            </div>
            <span class="badge">
              {% if request.user.is_staff %}مدیریت{% elif request.user.teacher_profile %}استاد{% else %}کاربر{% endif %}
            </span>"""

if target_menu in content:
    content = content.replace(target_menu, replacement_menu, 1)
    print("Added teacher portal to sidebar")
else:
    # Normalize CRLF
    target_menu_crlf = target_menu.replace("\n", "\r\n")
    replacement_menu_crlf = replacement_menu.replace("\n", "\r\n")
    if target_menu_crlf in content:
        content = content.replace(target_menu_crlf, replacement_menu_crlf, 1)
        print("Added teacher portal to sidebar (CRLF)")
    else:
        print("Warning: target_menu not found")

if old_user_card in content:
    content = content.replace(old_user_card, new_user_card, 1)
    print("Updated user card in footer")
else:
    old_user_card_crlf = old_user_card.replace("\n", "\r\n")
    new_user_card_crlf = new_user_card.replace("\n", "\r\n")
    if old_user_card_crlf in content:
        content = content.replace(old_user_card_crlf, new_user_card_crlf, 1)
        print("Updated user card in footer (CRLF)")
    else:
        print("Warning: old_user_card not found")

with open(base_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Updated dashboard/base.html")
