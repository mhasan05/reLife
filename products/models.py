from django.db import models
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
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name





class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    product_description = models.TextField(blank=True, null=True)
    product_image = models.ImageField(upload_to='product_images/')
    sku = models.CharField(max_length=100, unique=True, editable=False)
    company_id = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='company')
    category_id = models.ManyToManyField(Category, related_name='products', blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    discount_percent = models.PositiveIntegerField(default=0)  # Percentage discount (0-100)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Base price before discount
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum Retail Price
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

    @staticmethod
    def generate_unique_sku():
        """
        Generates a unique SKU using UUID and ensures it is unique within the database.
        """
        while True:
            new_sku = str(uuid.uuid4()).split('-')[0].upper()  # Generate a short unique string
            if not Product.objects.filter(sku=new_sku).exists():
                return new_sku

    def discount(self):
        """
        Returns the price after applying the percentage discount.
        """
        discount_amount = (self.mrp * self.discount_percent) / 100
        return discount_amount

    def selling_price(self):
        """
        Returns the final price (used in templates or views).
        """
        discount_amount = (self.mrp * self.discount_percent) / 100
        return self.mrp - discount_amount




