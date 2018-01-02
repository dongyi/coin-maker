from enum import Enum
from collections import defaultdict


class Event:

    def __init__(self, event_type, **kwargs):
        self.__dict__ = kwargs
        self.event_type = event_type

    def __repr__(self):
        return ' '.join('{}:{}'.format(k, v) for k, v in self.__dict__.items())


class EventBus:

    def __init__(self):
        self._listeners = defaultdict(list)

    def add_listener(self, event, listener):
        self._listeners[event].append(listener)

    def prepend_listener(self, event, listener):
        self._listeners[event].insert(0, listener)

    def publish_event(self, event):
        for l in self._listeners[event.event_type]:
            if l(event):
                break


class EVENT(Enum):

    ON_TICK = 'on_tick'
    ON_TRADE = 'on_trade'


def parse_event(event_str):
    return EVENT.__members__.get(event_str.upper(), None)
