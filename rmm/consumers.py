import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RemoteDesktopConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # The URL will be /ws/remote/AGENT_ID/
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.room_group_name = f"remote_{self.agent_id}"

        # Join the "Room" for this specific computer
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (Browser or Agent)
    async def receive(self, text_data=None, bytes_data=None):
        # If we receive bytes (Image data from Agent), send to Browser
        if bytes_data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_frame',
                    'bytes': bytes_data,
                    'sender_channel_name': self.channel_name
                }
            )
        
        # If we receive text (Mouse/Keyboard from Browser), send to Agent
        if text_data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'control_command',
                    'text': text_data,
                    'sender_channel_name': self.channel_name
                }
            )

    # Handler: Send Video Frame to Browser
    async def video_frame(self, event):
        # Don't send the frame back to the sender (the Agent)
        if self.channel_name != event['sender_channel_name']:
            await self.send(bytes_data=event['bytes'])

    # Handler: Send Control Command to Agent
    async def control_command(self, event):
        # Don't send the command back to the sender (the Browser)
        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=event['text'])