# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.db import models
from .models import UserAuth



class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = UserAuth.objects.get(models.Q(email=phone) | models.Q(phone=phone))
        except UserAuth.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
