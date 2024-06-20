import typing
from django.db import models
from rest_framework import permissions, exceptions

M = typing.TypeVar("M", bound=models.Model)


class _BaseApiFunctionViewModelPermissions(permissions.BasePermission):
    model = None

    perms_map = {
        "GET": [],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method):
        """Given a models and an HTTP method, return the list of permission codes that the user is required to have."""
        # noinspection PyProtectedMember Todo
        kwargs = {
            "app_label": self.model._meta.app_label,
            "model_name": self.model._meta.model_name,
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        perms = self.get_required_permissions(request.method)

        return request.user.has_perms(perms)


def permissions_for(model: typing.Generic[M]) -> type:
    """
    Create a dynamic permission class for the given model.

    Parameters:
        model: The model object for which the permissions class is being generated.

    Returns:
        type: The dynamically created permission class.
    """
    return type(
        f"{model.__class__.__name__}ModelPermission",
        (_BaseApiFunctionViewModelPermissions,),
        locals(),
    )
