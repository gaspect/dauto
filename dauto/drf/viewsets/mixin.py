from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class ByOperationSerializerMixin:
    """
    This class is responsible for determining the appropriate serializer class based on the HTTP request method
    and the action being performed. It extends the GenericViewSet class.
    """

    # noinspection PyUnresolvedReferences
    def get_serializer_class(self: viewsets.GenericViewSet):
        old: dict = super().get_serializer_class()
        if hasattr(self, "action") and self.action in old:
            return old.get(self.action)
        elif self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return old.get("read")
        return old.get("write")


class ByVersionSerializerMixin:
    """
    This class is responsible for determining the appropriate serializer class based on the request version.
    """

    # noinspection PyUnresolvedReferences
    def get_serializer_class(self):
        old: dict = super().get_serializer_class()
        return old.get(self.request.version)


# noinspection PyUnresolvedReferences
class CreateVerboseModelMixin(mixins.CreateModelMixin):
    """This class is a mixin that extends the functionality of the CreateModelMixin class. It provides additional
    methods for handling the creation of objects with verbose output."""

    # noinspection PyMethodMayBeStatic
    def get_read_object(self, instance):
        return instance

    def get_read_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        method = self.request.method
        self.request.method = "GET"
        serializer_class = self.get_serializer_class()
        self.request.method = method
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        read_serializer = self.get_read_serializer(self.get_read_object(serializer.instance))
        return Response(
            read_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


# noinspection PyUnresolvedReferences
class UpdateVerboseModelMixin(mixins.UpdateModelMixin):
    """
    This class is a mixin that provides additional functionality for updating models with verbose output.
    """

    # noinspection PyMethodMayBeStatic
    def get_read_object(self, instance):
        return instance

    def get_read_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        method = self.request.method
        self.request.method = "GET"
        serializer_class = self.get_serializer_class()
        self.request.method = method
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        read_serializer = self.get_read_serializer(self.get_read_object(serializer.instance))
        return Response(read_serializer.data)
