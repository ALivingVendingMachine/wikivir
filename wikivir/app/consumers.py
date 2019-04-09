# most of this code from https://github.com/arocks/channels-example/blob/master/show-notes.md
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("~~~~~CONN~~~~~")
        self.group_name = str(self.scope['url_route']['kwargs']['path'])

        # Send the connection
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'conn',
                'code': 'conn',
            }
        )

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("~~~~~DISC~~~~~")
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("~~~~~RECV~~~~~")
        message = text_data

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'code': 'recv',
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print("~~~~~MSG!~~~~~")
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'code': 'message',
        }))

    # Receive message from room group
    async def conn(self, event):
        print("~~~~~CONN~~~~~")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'code': 'conn',
        }))
