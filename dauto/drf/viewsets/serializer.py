from rest_framework import viewsets


class ByOperationSerializer:
    """
    Description:
        This class is responsible for determining the appropriate serializer class based on the HTTP request method
        and the action being performed. It extends the GenericViewSet class.

    Returns:
        The serializer class to be used for the current request and action.
    """

    # noinspection PyUnresolvedReferences
    def get_serializer_class(self: viewsets.GenericViewSet):
        old: dict = super().get_serializer_class()
        if hasattr(self, "action") and self.action in old:
            return old.get(self.action)
        elif self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return old.get("read")
        return old.get("write")


class ByVersionSerializer:
    """
    Description:
        This class is responsible for determining the appropriate serializer class based on the request version.

    Returns:
        The serializer class corresponding to the request version.

    """

    # noinspection PyUnresolvedReferences
    def get_serializer_class(self):
        old: dict = super().get_serializer_class()
        return old.get(self.request.version)
