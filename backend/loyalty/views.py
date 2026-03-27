from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from decimal import Decimal, InvalidOperation as DecimalException
from .models import Customer, LoyaltyPoint, Coupon, Campaign

from .serializers import CustomerSerializer, LoyaltyPointSerializer, CouponSerializer, CampaignSerializer
from users.permissions import IsStaff

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsStaff]

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        campaign = self.get_object()
        
        # Update multiplier if provided in request
        multiplier = request.data.get('multiplier')
        if multiplier is not None:
            try:
                campaign.multiplier = Decimal(str(multiplier))
            except (ValueError, TypeError, DecimalException):
                return Response({"error": "قيمة المضاعف غير صالحة."}, status=status.HTTP_400_BAD_REQUEST)
        
        campaign.is_active = not campaign.is_active
        campaign.save()
        return Response({
            'status': 'success',
            'is_active': campaign.is_active,
            'multiplier': campaign.multiplier,
            'message': f"تم {'تفعيل' if campaign.is_active else 'إلغاء تفعيل'} الحملة بنجاح."
        })


    @action(detail=False, methods=['get'])
    def active(self, request):
        campaign = Campaign.get_active_campaign()
        if not campaign:
            return Response(None, status=status.HTTP_200_OK)
        return Response(CampaignSerializer(campaign).data)



class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsStaff]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get analytics for the loyalty program."""
        # الأكثر زيارة (based on count of orders)
        most_visited = Customer.objects.annotate(
            visits=Count('orders')
        ).order_by('-visits')[:5]

        # الأكثر إنفاقاً
        highest_spending = Customer.objects.annotate(
            visits=Count('orders')
        ).order_by('-total_spent')[:5]

        # إحصائيات عامة
        total_points_redeemed = LoyaltyPoint.objects.filter(
            transaction_type=LoyaltyPoint.TransactionType.REDEEMED
        ).aggregate(total=Sum('points'))['total'] or 0

        coupons_used_count = Coupon.objects.filter(used_at__isnull=False).count()

        return Response({
            'most_visited': CustomerSerializer(most_visited, many=True).data,
            'highest_spending': CustomerSerializer(highest_spending, many=True).data,
            'total_points_redeemed': total_points_redeemed,
            'coupons_used_count': coupons_used_count,
            'total_customers': Customer.objects.count()
        })

class LoyaltyPointViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyPoint.objects.all()
    serializer_class = LoyaltyPointSerializer
    permission_classes = [IsStaff]

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsStaff]
