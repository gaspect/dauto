# # Utils

# A set of utilities functions that solve commons issues not precisely related to Django.
# These are:


# - dynamic import
# - turn functions in coroutines
# - make singleton classes
# - an event bus system.


from .using import using
from .awaitable import awaitable
from .singleton import singleton
from .events import Event, EventBus

__all__ = ("using", "awaitable", "singleton", "Event", "EventBus")
