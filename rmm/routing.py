from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/remote/(?P<agent_id>\w+)/$', consumers.RemoteDesktopConsumer.as_asgi()),
]