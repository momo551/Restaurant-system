from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TableViewSet, ReservationViewSet, TableSessionViewSet

router = DefaultRouter()
router.register('', TableViewSet, basename='tables')
router.register('reservations', ReservationViewSet, basename='reservations')
router.register('sessions', TableSessionViewSet, basename='table-sessions')

urlpatterns = [
    path('', include(router.urls)),
]
