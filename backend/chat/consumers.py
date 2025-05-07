import datetime
import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from .tasks import save_message_to_db


r = redis.StrictRedis(host="127.0.0.1", port=6379, db=0, decode_responses=True)


class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Testing Connection and Redis")

        request_user = self.scope['user']

        print(request_user, "USER")

        if request_user.is_authenticated:
            chat_with_user = self.scope['url_route']['kwargs']['id']
            user_ids = [int(request_user.id), int(chat_with_user)]
            user_ids = sorted(user_ids)

            self.room_group_name = f"chat_{user_ids[0]}-{user_ids[1]}"

            # ✅ Corrected: was 'group_app', should be 'group_add'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()  # ✅ Moved inside the if block
        else:
            # Optional: send a specific close code for unauthenticated users
            await self.close(code=4001)

    async def disconnect(self, code):
        # ✅ Corrected: added 'await'
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # this function is used to get message from client to server

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print(data)
        message = data['message']
        sender = self.scope['user'].id
        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()

        message_data = {
            "room": self.room_group_name,
            "sender_id": sender,
            "message": message,
            "timestamp": current_time
        }

        r.zadd(f"chat:messages:{self.room_group_name}",
               {json.dumps(message_data): current_time})

        # Get all messages
        messages = r.zrange(f"chat:messages:{self.room_group_name}", 0, -1)
        all_messages = [json.loads(message) for message in messages]

        # Trigger the Celery task to save the message to the DB
        save_message_to_db.delay(self.room_group_name,
                                 json.dumps(message_data))

        print(all_messages)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender
            }
        )

    # this function is used for sending message from server to all client (i.e. broadcast)
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        if self.scope['user'].id != sender:
            await self.send(text_data=json.dumps({
                "message": message
            }))
