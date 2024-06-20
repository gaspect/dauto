import typing
import functools
import asyncio
import inspect
import re
from dataclasses import dataclass
from datetime import datetime
from .singleton import singleton
from .awaitable import awaitable


_T = typing.TypeVar('_T')


@dataclass(frozen=True)
class Event(typing.Generic[_T]):
    topic: str
    payload: _T
    version: str | None = None
    date: datetime.date = datetime.now()


class _Observer:
    def __init__(self, topic, function: typing.Callable):
        self._topic = re.compile(topic)
        self._function = function
        functools.update_wrapper(self, self._function)

    @property
    def topic(self):
        return self._topic

    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)


@singleton
class EventBuss:
    observers: typing.List[_Observer]

    def __init__(self):
        self.observers = []

    def subscribe(self, topic: str):
        def decorator(callback: typing.Callable[[Event], typing.Awaitable[typing.Any]]):
            if not inspect.iscoroutinefunction(callback):
                callback = awaitable(callback)
            self.observers.append(_Observer(
                topic.replace('.', '\\.').replace('*', '.*'),
                callback
            ))
            return callback

        return decorator

    async def _dispatch(self, event: Event):
        coroutines = []
        for callbacks in self.observers:
            if callbacks.topic.fullmatch(event.topic):
                coroutines.append(callbacks(event))
        return await asyncio.gather(*coroutines)

    def dispatch(self, event: Event):
        return asyncio.run(self._dispatch(event))  # allow concurrent event handling
