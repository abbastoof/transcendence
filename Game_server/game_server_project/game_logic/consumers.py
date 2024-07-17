import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Consumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # Process keypress event
        if text_data_json.get('type') == 'keypress':
            key = text_data_json['key']
            code = text_data_json['code']
            key_code = text_data_json['keyCode']
            alt_key = text_data_json['altKey']
            ctrl_key = text_data_json['ctrlKey']
            shift_key = text_data_json['shiftKey']

            # Do something with the key press data
            print(f"Key pressed: {key}, Code: {code}, KeyCode: {key_code}, Alt: {alt_key}, Ctrl: {ctrl_key}, Shift: {shift_key}")

            # Send a response back to the client
            await self.send(text_data=json.dumps({
                'message': f"Key {key} pressed"
            }))