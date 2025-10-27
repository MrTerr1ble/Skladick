import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from skladick.apps.thresholds import routing as thresholds_routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skladick.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            thresholds_routing.websocket_urlpatterns
        )
    ),
})
