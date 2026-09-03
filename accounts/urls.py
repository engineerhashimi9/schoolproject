from django.urls import path
from .views import *


app_name = "accounts"
urlpatterns = [
    path("", login_view, name="login"),
    path("logout", custom_logout, name="logout")

]
