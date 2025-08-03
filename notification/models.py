from django.db import models
from accounts.models import UserAuth

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
