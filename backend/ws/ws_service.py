from enum import Enum

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings


class ObjectType(Enum):
    POST = 'Post'
    STAT = 'Stat'
    LAST_SYNC_DATE = 'LastSyncDate'


class EventType(Enum):
    CREATE = 'Create'
    UPDATE = 'Update'
    REMOVE = 'Remove'


def main_group_send(data: any, object_type: ObjectType, event_type: EventType = EventType.UPDATE):
    return async_to_sync(get_channel_layer().group_send)(
        settings.WS_MAIN_GROUP_NAME,
        {
            'type': 'app.activity',
            'object_type': object_type.value,
            'event_type': event_type.value,
            'body': data
        }
    )
