from django.db import models
import uuid
from accounts.models import UserAuth
import uuid
class Company(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.company_name
    

class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    


class GenericName(models.Model):
    generic_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Generic Name"
        ordering = ['name']

    def __str__(self):
        return self.name





class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    generic_name = models.ForeignKey(
        GenericName, 
        on_delete=models.SET_NULL,  # or CASCADE depending on your needs
        blank=True, 
        null=True,
        related_name='products'
    )
    product_description = models.TextField(blank=True, null=True)
    product_image = models.ImageField(upload_to='product_images/')
    sku = models.CharField(max_length=100, unique=True, editable=False)
    quantity_per_box = models.PositiveIntegerField(default=0)
    company_id = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='company')
    category_id = models.ManyToManyField(Category, related_name='products', blank=True)
    stock_quantity = models.IntegerField(default=0)
    discount_percent = models.PositiveIntegerField(default=0)  # Percentage discount (0-100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Base price before discount
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum Retail Price
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Final price after discount
    out_of_stock = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['product_name']

    def __str__(self):
        return self.product_name
    
    def save(self, *args, **kwargs):
        if not self.sku:  # Check if the SKU is empty
            self.sku = self.generate_unique_sku()
        super().save(*args, **kwargs)

    

    def save(self, *args, **kwargs):
    # Generate SKU if not present
        if not self.sku:
            new_sku = str(uuid.uuid4()).split('-')[0].upper()  # Generate a short unique string
            if not Product.objects.filter(sku=new_sku).exists():
                self.sku = new_sku

        # Auto-calculate discount percentage
        if self.mrp and self.selling_price and self.mrp > 0:
            self.discount_percent = round(((self.mrp - self.selling_price) / self.mrp) * 100)

        super().save(*args, **kwargs)



class BannerImages(models.Model):
    banner_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='banner_images')
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class TempProduct(models.Model):
    batch_id = models.UUIDField(editable=False, db_index=True)
    user_id = models.ForeignKey(UserAuth, on_delete=models.CASCADE)  # Track which admin is editing
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="pending_updates")
    new_stock_quantity = models.PositiveIntegerField(default=0)
    new_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    new_selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_on = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)  # Mark once applied

    def __str__(self):
        return str(self.batch_id)

    class Meta:
        verbose_name_plural = "Temp Products"
        ordering = ['product_id']

    def save(self, *args, **kwargs):
        # Auto-calculate total cost
        if self.new_cost_price and self.new_stock_quantity > 0:
            self.total_amount = self.new_cost_price * self.new_stock_quantity
        super().save(*args, **kwargs)