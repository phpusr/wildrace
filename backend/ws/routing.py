from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/wild-race/', consumers.AppConsumer)
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )
})
