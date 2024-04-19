import inspect
from django.db.models import Model
from django.contrib import admin


def register(container):
    """
    Registers models with the admin interface.

    Parameters:
    - container: A container object which holds the model classes to be registered.

    Returns:
    None

    Note:
    - This method will iterate over all the members of the 'container' object using `inspect.getmembers`.
    - It will check if each member is a class that inherits from 'Model' and has an 'Admin' attribute.
    - If the 'Admin' attribute exists and is a subclass of 'admin.ModelAdmin', the model will be registered using the 'admin.register' method.
    - If any error occurs during the registration process, a warning will be printed.

    Example usage:
    register(container) # Register all models in the container with the admin interface
    """
    for _, klass in inspect.getmembers(container):
        if (
            inspect.isclass(klass)
            and issubclass(klass, Model)
            and getattr(klass, "Admin", False)
            and issubclass(klass.Admin, admin.ModelAdmin)
        ):
            # noinspection PyBroadException
            try:
                admin.register(klass)(getattr(klass, "Admin"))
            except Exception:
                print(f"Model {klass.__name__} tried to be on admin but was ignored.")
