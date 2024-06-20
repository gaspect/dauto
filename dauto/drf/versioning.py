from rest_framework.versioning import NamespaceVersioning


class CustomNamespaceVersioning(NamespaceVersioning):
    """
    This class extends the NamespaceVersioning class and provides a custom implementation for versioning view names
    in a web application.
    """
    separator: str = '#'

    # noinspection SpellCheckingInspection
    def get_versioned_viewname(self, viewname: str, request):
        if self.separator in viewname:
            view, version = viewname.split(self.separator, maxsplit=1)
            return f"{version}:{view}"
        return super().get_versioned_viewname(viewname, request)
