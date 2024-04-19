import importlib


def attr(path: str):
    """
    Retrieve an attribute from a module.

    :param path: The fully qualified path of the attribute, in the format 'module_name.class_name'.
    :type path: str

    :raises ImportError: If the module or class could not be imported.

    :returns: The attribute object.
    """
    try:
        module_name, class_name = path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ImportError:
        raise
