# # Events

import typing
import functools
import inspect
import re
import threading
import asyncio
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


# Then the bus definition almost self-explanatory
class EventBus:
    observers: typing.List[_Observer]

    def __init__(self):
        self.observers = []
        # In thread safe environments like Django, run coroutines can be tricky, this is a 'just go' solution for it
        # with te proper use of event loops
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._start_event_loop, args=(self._loop,), daemon=True)
        self._loop_thread.start()

    @staticmethod
    def _start_event_loop(loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

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
        return asyncio.run_coroutine_threadsafe(self._dispatch(event), self._loop)  # allow concurrent event handling

    def __del__(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._loop_thread.join()

