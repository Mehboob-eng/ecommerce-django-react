from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product
from django.apps import apps


class Review(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    rating = models.PositiveSmallIntegerField()  # 1–5
    title = models.CharField(max_length=120, blank=True)
    body = models.TextField(max_length=2000)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    is_verified_purchase = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'product')]  # 1 review per product per user (optional)
        indexes = [
            models.Index(fields=['product', 'status', '-created_at']),
        ]

    def __str__(self):
        u = self.user or "Anon"
        return f"Review {self.id} · {self.product} · {u}"

    def _auto_verify_purchase(self):
        """
        Mark as verified if an order exists for this user+product with delivered status.
        Safe if orders app isn't present.
        """
        if not self.user_id:
            return
        try:
            Order = apps.get_model('orders', 'Order')
        except Exception:
            return
        if Order.objects.filter(user_id=self.user_id, product_id=self.product_id, status='delivered').exists():
            self.is_verified_purchase = True

    def save(self, *args, **kwargs):
        # ensure rating 1..5
        if self.rating < 1: self.rating = 1
        if self.rating > 5: self.rating = 5
        if not self.is_verified_purchase:
            self._auto_verify_purchase()
        super().save(*args, **kwargs)
