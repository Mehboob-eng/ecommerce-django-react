from decimal import Decimal, ROUND_HALF_UP
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from .models import Order

def money(x):
    return Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'product__name', 'address')
    readonly_fields = ('price', 'created_at', 'idempotency_key')
    autocomplete_fields = ('user', 'product')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)
        if obj:
            ro += ['user', 'product']  # lock after create
        return ro

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """
        - CREATE: check stock, compute price inline, decrement stock
        - EDIT qty (only while pending): adjust stock delta and recompute price
        - CANCEL: restock once; can't edit cancelled orders
        """
        if not change:
            if obj.quantity < 1:
                raise ValidationError("Quantity must be at least 1.")
            if getattr(obj.product, 'stock', 0) < obj.quantity:
                raise ValidationError("Not enough stock for this product.")

            # compute price here (no calculate_total() dependency)
            unit = money(obj.product.price)
            obj.price = unit * obj.quantity

            super().save_model(request, obj, form, change)

            # decrement stock
            type(obj.product).objects.filter(id=obj.product_id).update(stock=F('stock') - obj.quantity)
            return

        # EDIT
        existing = Order.objects.select_for_update().get(pk=obj.pk)

        if existing.status == Order.Status.CANCELLED:
            raise ValidationError("Cancelled orders cannot be edited.")

        qty_changed = obj.quantity != existing.quantity
        status_changed = obj.status != existing.status

        if qty_changed and existing.status != Order.Status.PENDING:
            raise ValidationError("Only pending orders can change quantity.")

        # quantity delta handling
        if qty_changed:
            if obj.quantity < 1:
                raise ValidationError("Quantity must be at least 1.")
            delta = obj.quantity - existing.quantity
            if delta > 0:
                if getattr(existing.product, 'stock', 0) < delta:
                    raise ValidationError("Not enough stock to increase quantity.")
                type(existing.product).objects.filter(id=existing.product_id).update(stock=F('stock') - delta)
            elif delta < 0:
                type(existing.product).objects.filter(id=existing.product_id).update(stock=F('stock') + (-delta))

        # status transitions
        if status_changed:
            if obj.status == Order.Status.CANCELLED:
                if existing.status != Order.Status.PENDING:
                    raise ValidationError("Only pending orders can be cancelled.")
                type(existing.product).objects.filter(id=existing.product_id).update(stock=F('stock') + obj.quantity)

        # recompute price if qty changed
        if qty_changed:
            unit = money(existing.product.price)
            obj.price = unit * obj.quantity
        else:
            obj.price = existing.price

        super().save_model(request, obj, form, change)
