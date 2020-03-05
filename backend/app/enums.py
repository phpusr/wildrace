from enum import Enum


class ObjectType(Enum):
    POST = 'Post'
    STAT = 'Stat'
    LAST_SYNC_DATE = 'LastSyncDate'


class EventType(Enum):
    CREATE = 'Create'
    UPDATE = 'Update'
    REMOVE = 'Remove'
