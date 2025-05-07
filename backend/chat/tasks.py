import datetime
from celery import shared_task
from django.utils import timezone
from .models import ChatMessage, User, Room
import json
import redis

r = redis.StrictRedis(host="127.0.0.1", port=6379, db=0, decode_responses=True)


@shared_task
def save_message_to_db(room_name, message_data):
    print("here")
    try:
        message = json.loads(message_data)
        sender_id = message.get('sender_id')
        sender = User.objects.get(id=sender_id)
        timestamp = timezone.make_aware(
            datetime.datetime.fromtimestamp(message.get('timestamp')))

        room = Room.get_or_create_room(room_name)

        chat_message = ChatMessage(
            room=room,
            sender=sender,
            message=message.get('message'),
            timestamp=timestamp
        )

        chat_message.save()

    except Exception as e:
        print(f"Error saving Message to DB: {e}")
