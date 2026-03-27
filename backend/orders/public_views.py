from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from menu.models import Category, MenuItem, ProductOffer
from menu.serializers import CategorySerializer, ProductOfferSerializer
from .models import Order
from .serializers import OrderSerializer
from loyalty.models import Campaign, Customer, Coupon
from loyalty.serializers import CampaignSerializer, CustomerSerializer
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
class PublicMenuView(APIView):
    """View to fetch the full menu for public customers."""
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes in Redis
    def get(self, request):
        categories = Category.objects.filter(is_active=True, is_deleted=False).prefetch_related('items')
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class PublicOrderTrackView(APIView):
    """View to track an order status."""
    permission_classes = [AllowAny]

    def get(self, request, order_number):
        phone = request.query_params.get('phone')
        if not phone:
            return Response({"error": "Phone number is required for tracking."}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.db.models import Q
        order = get_object_or_404(
            Order, 
            Q(order_number=order_number) & (Q(customer_phone=phone) | Q(customer__phone=phone))
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class PublicCampaignView(APIView):
    """View to fetch the currently active campaign."""
    permission_classes = [AllowAny]

    def get(self, request):
        campaign = Campaign.get_active_campaign()
        if campaign:
            serializer = CampaignSerializer(campaign)
            return Response(serializer.data)
        return Response(None)


class PublicCustomerInfoView(APIView):
    """View to fetch customer info and points balance using phone number."""
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)


class PublicOffersView(APIView):
    """View to list all currently active product offers."""
    permission_classes = [AllowAny]

    def get(self, request):
        offers = ProductOffer.get_all_active_offers()
        serializer = ProductOfferSerializer(offers, many=True, context={'request': request})
        return Response(serializer.data)


class PublicApplyCouponView(APIView):
    """Validate a coupon code and return the discount amount."""
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        subtotal = request.data.get('subtotal', 0)

        if not code:
            return Response({"error": "كود الكوبون مطلوب."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subtotal = Decimal(str(subtotal))
        except Exception:
            return Response({"error": "قيمة المجموع غير صالحة."}, status=status.HTTP_400_BAD_REQUEST)

        coupon = Coupon.objects.filter(code=code, is_active=True).first()
        if not coupon:
            return Response({"error": "كود الكوبون غير صالح أو منتهي الصلاحية."}, status=status.HTTP_404_NOT_FOUND)

        if coupon.valid_until < timezone.now():
            return Response({"error": "انتهت صلاحية هذا الكوبون."}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.used_at:
            return Response({"error": "تم استخدام هذا الكوبون من قبل."}, status=status.HTTP_400_BAD_REQUEST)

        if subtotal < coupon.min_purchase:
            return Response({
                "error": f"الحد الأدنى للشراء لهذا الكوبون هو {coupon.min_purchase} جنيه."
            }, status=status.HTTP_400_BAD_REQUEST)

        if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
            discount = (subtotal * coupon.discount_amount / Decimal('100')).quantize(Decimal('0.01'))
        else:
            discount = min(coupon.discount_amount, subtotal)

        final_total = max(Decimal('0'), subtotal - discount)

        return Response({
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_amount": float(discount),
            "final_total": float(final_total),
            "message": f"تم تطبيق الكوبون! خصم {float(discount):.0f} جنيه 🎉"
        })


class PublicOrderCreateView(APIView):
    """View to create an order from the public website, supporting loyalty points & coupons."""
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        phone = request.data.get('customer_phone')
        if not phone:
            return Response({"error": "customer_phone is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create customer
        customer, created = Customer.objects.get_or_create(
            phone=phone,
            defaults={'name': request.data.get('customer_name', 'عميل')}
        )

        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order_type = serializer.validated_data.get('order_type')
            if order_type == Order.OrderType.DINE_IN:
                return Response(
                    {"error": "Public orders must be Delivery or Takeaway."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create order (serializer + model handle items, totals, points, and coupons)
            order = serializer.save(customer=customer)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
