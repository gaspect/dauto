# # Events

import typing
import functools
import asyncio
import inspect
import re
from dataclasses import dataclass
from datetime import datetime
from .awaitable import awaitable

# We have been found a lot of events definitions over internet. This is one of them.

_T = typing.TypeVar('_T')


@dataclass(frozen=True)
class Event(typing.Generic[_T]):
    topic: str
    payload: _T
    version: str | None = None
    date: datetime.date = datetime.now()


# Because we build the events system based on the observer pattern we need a sort of observer definition.

class _Observer:
    def __init__(self, topic, function: typing.Callable, version: str | None = None):
        self._topic = re.compile(topic)
        self._function = function
        self._version = version
        functools.update_wrapper(self, self._function)

    @property
    def topic(self):
        return self._topic

    @property
    def version(self):
        return self._version

    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)


# Then the buss definition almost self-explanatory
class EventBus:
    observers: typing.List[_Observer]

    def __init__(self):
        self.observers = []

    def subscribe(self, topic: str, version: str | None = None):
        """
        This function return a decorator to subscribe a handler to an event topic and version.

        Parameters:
            topic (str): The topic to subscribe to.
            version (str): The version to subscribe to.
        Returns:
              callable: A decorator to subscribe to an event topic and version.
        """
        def decorator(callback: typing.Callable[[Event], typing.Awaitable[typing.Any]]):
            if not inspect.iscoroutinefunction(callback):
                callback = awaitable(callback)
            self.observers.append(_Observer(
                topic.replace('.', '\\.').replace('*', '.*'),
                callback,
                version
            ))
            return callback

        return decorator

    async def _dispatch(self, event: Event):
        coroutines = []
        for callbacks in self.observers:
            if (callbacks.topic.fullmatch(event.topic) and
                    (callbacks.version is None or callbacks.version == event.version)):
                coroutines.append(callbacks(event))
        return await asyncio.gather(*coroutines)

    def dispatch(self, event: Event):
        """
        Dispatch an event.

        Parameters:
            event (Event): The event to dispatch.
        """
        return asyncio.run(self._dispatch(event))  # allow concurrent event handling
