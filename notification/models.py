from django.db import models
from accounts.models import UserAuth
from orders.models import Order

class Notification(models.Model):

    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.user.full_name or self.user.user_id} - {self.title}"
    



class AdminNotification(models.Model):

    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE, related_name='admin_notifications')
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='admin_notifications', null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Admin Notification to {self.user.full_name or self.user.user_id} - {self.title}"
