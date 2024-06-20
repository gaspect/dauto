import functools


def awaitable(func):
    """Wrap a synchronous callable to allow ``await``'ing it"""

    @functools.wraps(func)
    async def coroutine(*args, **kwargs):
        return func(*args, **kwargs)

    return coroutine
