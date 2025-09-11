from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils import timezone
from accounts.manager import UserManager


class District(models.Model):
    district_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Districts"
        ordering = ['name']

    def __str__(self):
        return self.name

class Area(models.Model):
    class Meta:
        verbose_name_plural = "Area"
    area_id = models.BigAutoField(primary_key=True)
    area_name = models.CharField(max_length=100, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="areas",null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.area_name

class UserAuth(AbstractBaseUser,PermissionsMixin):
    class Meta:
        verbose_name_plural = "User"
    user_id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    shop_address = models.CharField(max_length=500,null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email','full_name']

    objects = UserManager()

    def __str__(self):
        return self.full_name
    


class Address(models.Model):
    class Meta:
        verbose_name_plural = "Address"
    address_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure only one default address per user
        if self.is_default:
            Address.objects.filter(user_id=self.user_id, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.full_name)