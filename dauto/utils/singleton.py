import functools


def singleton(cls):
    """
    Make a class a singleton
    Parameters:
        cls (type): the class to be decorated
    """
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if wrapper_singleton.instance is None:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton
