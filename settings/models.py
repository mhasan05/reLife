from django.db import models

# Create your models here.
class SiteInfoModel(models.Model):
    name = models.CharField(max_length=100, default='BDM')
    version = models.CharField(max_length=10, default='1.0')
    description = models.TextField(default='A platform for managing orders.')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=1, default=80.0)
    contact_email = models.EmailField(default='info@bdm.com')
    contact_phone = models.CharField(max_length=15, default='1234567890')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.version}"