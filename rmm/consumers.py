import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RemoteDesktopConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.agent_id = self.scope['url_route']['kwargs']['agent_id']
        self.room_group_name = f"remote_{self.agent_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (Browser or Agent)
    async def receive(self, text_data=None, bytes_data=None):
        # 1. Handle Binary Data (Video Frames from Agent)
        if bytes_data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_frame',
                    'bytes': bytes_data,
                    'sender_channel_name': self.channel_name
                }
            )
        
        # 2. Handle Text Data (Commands or Mouse/Keyboard)
        if text_data:
            try:
                data = json.loads(text_data)
                msg_type = data.get('type', '')

                # If it's a shell command/output, use a specific handler
                if msg_type in ['shell_command', 'shell_output']:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'forward_shell',
                            'message': data,
                            'sender_channel_name': self.channel_name
                        }
                    )
                else:
                    # Default to control command (Mouse/Keyboard)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'control_command',
                            'text': text_data,
                            'sender_channel_name': self.channel_name
                        }
                    )
            except:
                pass

    # --- HANDLERS ---

    async def video_frame(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send(bytes_data=event['bytes'])

    async def control_command(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=event['text'])

    # New Handler for Shell
    async def forward_shell(self, event):
        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=json.dumps(event['message']))