import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings

from app.services.index_page_service import encode_json

logger = logging.getLogger(__name__)


class AppConsumer(JsonWebsocketConsumer):

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            settings.WS_MAIN_GROUP_NAME,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code: int):
        logger.debug('Socket disconnect with code', close_code)

    def app_activity(self, event: dict):
        self.send_json(event)

    @classmethod
    def encode_json(cls, content: dict):
        return encode_json(content)
