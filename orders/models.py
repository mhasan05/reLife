from django.db import models
from django.utils import timezone
from accounts.models import UserAuth  # Import User model from accounts app
from products.models import Product  # Import Product model from products app
import datetime
import random

from django.db.models.signals import post_save
from django.dispatch import receiver

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_id = models.BigAutoField(primary_key=True)
    invoice_number = models.CharField(max_length=20, unique=True,null=True, blank=True)  # Unique invoice number for the order
    user_id = models.ForeignKey(UserAuth, on_delete=models.CASCADE)  # Link to User model
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total price of the order
    shipping_address = models.CharField(max_length=255,null=True, blank=True)  # Shipping address for the order
    order_date = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ['-order_date']

    def __str__(self):
        return self.invoice_number

    def generate_invoice_number(self):
        """
        Generates a unique invoice number based on the current date and a random number.
        """
        date_part = datetime.datetime.now().strftime("%Y%m%d")
        random_part = random.randint(1000, 9999)
        return f"INV-{date_part}-{random_part}"

    def save(self, *args, **kwargs):
        # Generate a unique invoice number if it doesn't exist
        if not self.invoice_number:
            while True:
                new_invoice_number = self.generate_invoice_number()
                if not Order.objects.filter(invoice_number=new_invoice_number).exists():
                    self.invoice_number = new_invoice_number
                    break

        super().save(*args, **kwargs)


# # Signal to calculate total_amount after order is saved
# @receiver(post_save, sender=Order)
# def update_total_amount(sender, instance, **kwargs):
#     """
#     Updates the total amount of the order after it has been saved.
#     """
#     order_items = instance.items.all()  # Access related order items
#     total_price = sum([item.get_item_total() for item in order_items])
#     if instance.total_amount != total_price:
#         instance.total_amount = total_price
#         instance.save()




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Link to the Order
    product = models.ForeignKey(Product, on_delete=models.PROTECT)  # Link to the Product
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product in the order
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)  # Price at the time of order
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Order Items"
        ordering = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    def items_total(self):
        """
        Calculates the total price for this item based on quantity and unit price.
        """
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Ensure unit_price is set to the product's selling price when saving
        self.unit_price = self.product.selling_price  # Set the price to the selling price
        super().save(*args, **kwargs)





class Return(models.Model):
    RETURN_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    return_id = models.BigAutoField(primary_key=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='returns')  # Link to OrderItem
    quantity = models.PositiveIntegerField()  # Quantity being returned
    reason = models.TextField(blank=True, null=True)  # Optional reason for return
    status = models.CharField(max_length=10, choices=RETURN_STATUS_CHOICES, default='pending')  # Return status
    created_on = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(blank=True, null=True)
    processed_by = models.CharField(max_length=100, blank=True, null=True)  # Admin or staff who processed the return

    class Meta:
        verbose_name_plural = "Returns"
        ordering = ['-created_on']

    def __str__(self):
        return f"Return {self.return_id} - {self.order_item.product.product_name}"

    def is_valid_return(self):
        """
        Ensures that the return quantity does not exceed the ordered quantity.
        """
        if self.quantity > self.order_item.quantity:
            return False  # Cannot return more than ordered
        return True

    def process_return(self):
        """
        Handles return processing: updates order item quantity and marks the return as completed.
        """
        if self.status == 'approved' and self.is_valid_return():
            self.order_item.quantity -= self.quantity
            self.order_item.save()
            self.status = 'completed'
            self.processed_on = timezone.now()
            self.save()
