from django.contrib import admin
from .models import Customer, LoyaltyPoint, Coupon, Campaign

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'points_balance', 'total_spent', 'created_at')
    search_fields = ('name', 'phone')

@admin.register(LoyaltyPoint)
class LoyaltyPointAdmin(admin.ModelAdmin):
    list_display = ('customer', 'points', 'transaction_type', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('customer__name', 'customer__phone')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_amount', 'is_active', 'valid_until')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'multiplier', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
