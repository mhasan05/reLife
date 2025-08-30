from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Company)
admin.site.register(BannerImages)
admin.site.register(GenericName)
admin.site.register(TempProduct)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_on']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'get_categories', 'company_id','quantity_per_box', 'mrp', 'stock_quantity', 'is_active']
    list_filter = ['company_id', 'is_active']
    search_fields = ['product_name', 'sku']

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.category_id.all()])
    get_categories.short_description = 'Categories'  # Sets the column header in the admin list view
