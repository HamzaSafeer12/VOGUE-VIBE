from django.conf import settings
from django.db import models
from ..models import ProductVariant

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.variant.product.name} ({self.variant.size.name})"

    # Total price nikalne ke liye ek chota sa helper function
    def get_total_price(self):
        return self.quantity * self.variant.product.price