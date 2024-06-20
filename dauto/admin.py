# # Administration Site

import inspect
from django.db.models import Model
from django.contrib import admin


# This IS NOT a  module/guide to make your administration site more beautiful, useful or user-friendly. This is a
# guide to do a 'better' setups of admin classes.  What this mean? We aim to encapsulate each admin
# class definition inside his target model (because one is meaningless without the other) then with the following
# method and the model container/module path we can dynamically set up the administration site.

def register(container):
    """
    Registers models with the admin interface.

    Parameters:
        container: A container object which holds the model classes to be registered.
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
