from django.core.exceptions import ImproperlyConfigured
from rest_framework.throttling import SimpleRateThrottle


class ByOperationThrottle(SimpleRateThrottle):
    """
    Throttle mechanism based on DRF SimpleRateThrottle. Check the documentation for further details.

    https://www.django-rest-framework.org/api-guide/throttling/#custom-throttles

    Throttle for mapping view operations to a custom rate throttle. The view or viewset must define a `throttle_scope` attribute to map actions to specific rate limits.
    Just add this field to the view:

    throttle_scopes = {
        'list': '10/m'
        'retrieve': '10/m'

        # Other actions
        ...
    }

    Can be combined with other Throttle classes like UserRateThrottle or AnonRateThrottle.

    class ByOperationUserRateThrottle(ByOperationThrottle, UserRateThrottle):
        pass

    class ByOperationAnonRateThrottle(ByOperationThrottle, AnonRateThrottle):
        pass
    """

    scope = "by-operation"  # default scope
    rate = "50/m"  # default rate limit

    def allow_request(self, request, view):
        # Override init scope and rate before checking for request
        self._override_scope(request, view)
        self._override_rate(request, view)
        return super().allow_request(request, view)

    def _override_scope(self, request, view):
        self.scope = self._get_scope(request, view)

    def _override_rate(self, request, view) -> None:
        self.rate = self._get_rate(request, view)
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def _get_operation(self, request, view) -> str:
        if hasattr(view, "action"):
            return getattr(view, "action")
        elif request.method in ["GET", "HEAD", "OPTIONS"]:
            return "read"

        return "write"

    def _get_scope(self, request, view) -> str:
        return f"{self._get_operation(request, view)}-{self._get_scope_suffix(request, view)}"

    def _get_rate(self, request, view) -> str | None:
        scopes = self._get_view_scopes(view)
        return scopes.get(self._get_operation(request, view), None)

    def _get_scope_suffix(self, request, view) -> str | None:
        """
        Retrieves the scope suffix. Usually extracted from the view model queryset
        """

        queryset = getattr(view, "queryset", None)
        if queryset is None:
            return ""

        return queryset.model._meta.model_name

    def _get_view_scopes(self, view) -> dict[str, str]:
        if not hasattr(view, "throttle_scopes"):
            raise ImproperlyConfigured(
                f"Missing throttle_scopes attribute in view {view.__class__.__name__}"
            )

        return getattr(view, "throttle_scopes", {})