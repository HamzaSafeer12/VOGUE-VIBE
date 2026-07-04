from django.db import models
from django.contrib.auth.models import User # Django ka built-in user

class Profile(models.Model):
    # 'OneToOneField' ka matlab hai har User ka sirf EK profile hoga
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"