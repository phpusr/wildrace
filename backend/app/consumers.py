from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings

from app.enums import ObjectType, EventType
from app.services.index_page_service import encode_json


class AppConsumer(JsonWebsocketConsumer):

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            settings.WS_MAIN_GROUP_NAME,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code: int):
        print('>> Socket disconnect with code', close_code)

    def app_activity(self, event: dict):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content: dict):
        return encode_json(content)


def main_group_send(data: any, object_type: ObjectType, event_type: EventType):
    return async_to_sync(get_channel_layer().group_send)(
        settings.WS_MAIN_GROUP_NAME,
        {
            'type': 'app.activity',
            'object_type': object_type.value,
            'event_type': event_type.value,
            'body': data
        }
    )
