from django.urls import path
from .public_views import (
    PublicMenuView, 
    PublicOrderCreateView, 
    PublicOrderTrackView,
    PublicCampaignView,
    PublicCustomerInfoView,
    PublicOffersView,
    PublicApplyCouponView,
)

urlpatterns = [
    path('menu/', PublicMenuView.as_view(), name='public-menu'),
    path('orders/', PublicOrderCreateView.as_view(), name='public-order-create'),
    path('track/<str:order_number>/', PublicOrderTrackView.as_view(), name='public-order-track'),
    path('loyalty/campaigns/active/', PublicCampaignView.as_view(), name='public-campaign-active'),
    path('loyalty/customer-info/', PublicCustomerInfoView.as_view(), name='public-customer-info'),
    path('offers/', PublicOffersView.as_view(), name='public-offers'),
    path('apply-coupon/', PublicApplyCouponView.as_view(), name='public-apply-coupon'),
]
