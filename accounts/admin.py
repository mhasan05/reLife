from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group

class UserAuthAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'is_approved', 'created_on')
    
    search_fields = ('full_name', 'email', 'phone')
    
    ordering = ('phone',)

    fieldsets = (
        ('Profile', {
            'fields': ('full_name', 'email', 'phone', 'image')
        }),
        ('Shop', {
            'fields': ('shop_name', 'shop_address', 'area')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_approved', 'is_staff', 'is_superuser')
        }),
    )

admin.site.register(UserAuth, UserAuthAdmin)
admin.site.register(Address)
admin.site.register(Area)
admin.site.unregister(Group)