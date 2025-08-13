from django.db import models
from decimal import Decimal , ROUND_HALF_UP
from django.conf import settings
from django.utils import timezone
from products.models import Product


def money(x):
    return Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    # Final price stored at order time = product.price * quantity (immutable after create)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    address = models.TextField(max_length=500)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    # Optional idempotency key to prevent accidental duplicate orders
    idempotency_key = models.CharField(max_length=64, null=True, blank=True, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return f"Order {self.id} - {self.user}"
    def calculat_total(self):
        return self.product.price * self.quantity
    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.calculat_total()
        super().save(*args, **kwargs)
    @property
    def total(self) -> Decimal:
        # price already includes qty at create time, but expose total for clarity
        return self.price
