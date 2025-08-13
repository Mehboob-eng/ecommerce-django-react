from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'status', 'is_verified_purchase', 'created_at')
    list_filter = ('status', 'rating', 'is_verified_purchase', 'created_at', 'product')
    search_fields = ('id', 'product__name', 'user__username', 'title', 'body')
    autocomplete_fields = ('product', 'user')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('product', 'user', 'rating', 'title', 'body')}),
        ('Moderation', {'fields': ('status', 'is_verified_purchase')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"Approved {count} review(s).")
    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"Rejected {count} review(s).")
    reject_reviews.short_description = "Reject selected reviews"
