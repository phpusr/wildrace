from enum import Enum, unique, auto


@unique
class EventType(Enum):
    CREATE = auto()
    UPDATE = auto()
    REMOVE = auto()
