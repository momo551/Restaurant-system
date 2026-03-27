from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

class Customer(models.Model):
    """Customer profile for loyalty program."""
    name = models.CharField(max_length=200, verbose_name='اسم العميل')
    phone = models.CharField(max_length=20, unique=True, verbose_name='رقم الهاتف')
    email = models.EmailField(blank=True, null=True, verbose_name='البريد الإلكتروني')
    points_balance = models.PositiveIntegerField(default=0, verbose_name='رصيد النقاط')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='إجمالي المشتريات')
    last_visit = models.DateTimeField(auto_now=True, verbose_name='آخر زيارة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الانضمام')

    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone})"


class LoyaltyPoint(models.Model):
    """Tracks points earned or spent by a customer."""
    class TransactionType(models.TextChoices):
        EARNED = 'earned', 'مكتسبة'
        REDEEMED = 'redeemed', 'مستبدلة'
        EXPIRED = 'expired', 'منتهية'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_points', verbose_name='العميل')
    points = models.IntegerField(verbose_name='النقاط')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, verbose_name='نوع العملية')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الطلب المرتبط')
    description = models.CharField(max_length=255, blank=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')

    class Meta:
        verbose_name = 'نقطة ولاء'
        verbose_name_plural = 'نقاط الولاء'
        ordering = ['-created_at']



class Campaign(models.Model):
    """Time-limited loyalty campaigns (e.g., Double Points Weekend)."""
    name = models.CharField(max_length=200, verbose_name='اسم الحملة')
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0, verbose_name='مضاعف النقاط')
    start_date = models.DateTimeField(verbose_name='تاريخ البداية')
    end_date = models.DateTimeField(verbose_name='تاريخ النهاية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'حملة'
        verbose_name_plural = 'حملات'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} (x{self.multiplier})"

    @property
    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @classmethod
    def get_active_campaign(cls):
        now = timezone.now()
        return cls.objects.filter(is_active=True, start_date__lte=now, end_date__gte=now).first()


class Coupon(models.Model):
    """Discount coupons for customers."""
    class DiscountType(models.TextChoices):
        FIXED = 'fixed', 'ثابت'
        PERCENTAGE = 'percentage', 'نسبة مئوية'

    code = models.CharField(max_length=20, unique=True, verbose_name='كود الكوبون')
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.FIXED, verbose_name='نوع الخصم')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قيمة الخصم')

    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الحد الأدنى للشراء')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    valid_until = models.DateTimeField(verbose_name='صالح حتى')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupons', verbose_name='العميل (اختياري)')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الاستخدام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'كوبون'
        verbose_name_plural = 'الكوبونات'

    def __str__(self):
        return self.code
