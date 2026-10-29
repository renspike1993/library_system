import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from config.routing import application as routing_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = routing_application