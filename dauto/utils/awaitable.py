import functools


def awaitable(func):
    """
    Wrap a synchronous callable to allow ``await``'ing it

    Parameters:
        func (callable): function to be converted to awaitable
    """

    @functools.wraps(func)
    async def coroutine(*args, **kwargs):
        return func(*args, **kwargs)

    return coroutine
