from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now=True)

    def get_or_create_room(room_name):
        room, created = Room.objects.get_or_create(name=room_name)
        return room

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    room = models.ForeignKey(
        Room, related_name='messages', on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, related_name='sent_messages', on_delete=models.CASCADE
    )
    message = models.TextField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.room.name}:{self.sender.id}"
