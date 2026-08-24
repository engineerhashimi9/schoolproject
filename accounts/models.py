from typing import Any

from django.db import models

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

class UserManager(BaseUserManager) :
    def create_user(self, email,password,**kwargs) :
        if not email :
            raise ValueError("email must be set")
        email=self.normalize_email(email)
        user=self.model(email,**kwargs)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,email,password, **kwargs) :
        kwargs.setdefault("is_staff",True)
        kwargs.setdefault("is_verified",True)
        kwargs.setdefault("is_active",True)
        kwargs.setdefault("is_superuser",True)
        if not kwargs.get("is_superuser")  :
            raise ValueError("invalid operation")
        if not kwargs.get("is_staff")  :
            raise ValueError("invalid operation")
        return self.create_user(email,password,**kwargs)
        



class user(AbstractBaseUser,PermissionsMixin) :
    id=models.AutoField(primary_key=True)
    name=models.CharField( max_length=100)
    last_name=models.CharField( max_length=100)
    email=models.EmailField( max_length=254)
    created_date=models.DateTimeField( auto_now=False, auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    #configs
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "lastname","email"]
    objects=UserManager()


