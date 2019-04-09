from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from app.consumers import Consumer
#from app.consumers import Consumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/<str:path>", Consumer),
        #path("ws/", Consumer),
    ])
})