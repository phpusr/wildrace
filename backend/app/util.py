from datetime import datetime
from typing import Iterable, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone

from app.enums import ObjectType, EventType


def find(lst: Iterable, action):
    result = find_all(lst, action)
    if result:
        return result[0]


def find_all(lst: Iterable, action):
    return list(filter(action, lst))


def remove_non_utf8_chars(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None

    return bytes(text, 'utf-8').decode('utf-8', 'ignore')


def get_count_days(start_date: Optional[datetime], end_date: Optional[datetime]):
    if not start_date or not end_date:
        return None

    if start_date > end_date:
        raise RuntimeError('start_date > end_date')

    return (end_date - start_date).days + 1


def get_class(class_name: str) -> type:
    parts = class_name.split('.')
    module = '.'.join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def encode_json(content: dict) -> str:
    cl = get_class(settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'][0])
    return cl().render(content).decode('utf-8')


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


def date_to_js_unix_time(date: datetime) -> int:
    return int(date.timestamp() * 1000)


def js_unix_time_to_date(timestamp: int) -> datetime:
    return datetime.utcfromtimestamp(timestamp / 1000).astimezone(timezone.get_default_timezone())
