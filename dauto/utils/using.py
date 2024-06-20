import importlib


def using(path: str):
    """
    Retrieve an attribute from a module.

    Parameters:
        path (str): The fully qualified path of the attribute, in the format 'module_name.class_name'.

    Returns:
        any: The attribute object.

    Raises:
        ImportError: If the module or class could not be imported.
    """
    try:
        module_name, class_name = path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ImportError:
        raise
