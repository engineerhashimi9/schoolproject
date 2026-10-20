with open("core/settings.py", "r", encoding="utf-8") as f:
    c = f.read()

if '"teachers",' not in c:
    c = c.replace('"dashboard",', '"dashboard",\n    "teachers",')
    with open("core/settings.py", "w", encoding="utf-8") as f:
        f.write(c)
    print("SUCCESS: Added teachers to INSTALLED_APPS")
else:
    print("Already exists")
