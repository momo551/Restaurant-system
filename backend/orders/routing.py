from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/kds/$', consumers.KDSConsumer.as_asgi()),
    re_path(r'^ws/track/(?P<order_number>[\w-]+)/$', consumers.OrderTrackingConsumer.as_asgi()),
]
