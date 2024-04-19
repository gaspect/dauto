from rest_framework.versioning import NamespaceVersioning


class CustomNamespaceVersioning(NamespaceVersioning):
    """

    Class: CustomNamespaceVersioning

    This class extends the NamespaceVersioning class and provides a custom implementation for versioning view names in a web application.

    Attributes:
        separator (str): The separator used to split the view name and version in the get_versioned_viewname method.

    Methods:
        get_versioned_viewname(viewname: str, request) -> str:
            This method takes a view name and a request object as parameters and returns the versioned view name. If the view name contains the separator, it splits the view name and version using the separator attribute and returns the versioned view name in the format "{version}:{view}". If the view name does not contain the separator, it delegates the call to the parent class's get_versioned_viewname method.

    """
    separator: str = '#'

    # noinspection SpellCheckingInspection
    def get_versioned_viewname(self, viewname: str, request):
        if self.separator in viewname:
            view, version = viewname.split(self.separator, maxsplit=1)
            return f"{version}:{view}"
        return super().get_versioned_viewname(viewname, request)
