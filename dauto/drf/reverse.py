from urllib.parse import urlencode
from rest_framework.reverse import reverse as drf_reverse

# Django's `reverse` method in DRF does not provide a built-in way to generate URLs with query parameters.
# This utility function addresses that limitation by accepting a dictionary of query parameters
# and returning the generated URL with the parameters appended.

def reverse(
    view_name,
    request=None,
    urlconf=None,
    query_kwargs=None,
    kwargs=None,
):
    """
    Generate a URL with a query string.

    :param view_name: The name of the view
    :param request: The request object (optional)
    :param urlconf: The URL configuration (optional)
    :param query_kwargs: Dictionary of query parameters (optional)
    :param kwargs: Dictionary of view (path) arguments (optional)
    :return: The generated URL with query string
    """

    base_url = drf_reverse(view_name, request=request, urlconf=urlconf, kwargs=kwargs)
    if query_kwargs:
        return "{}?{}".format(base_url, urlencode(query_kwargs))
    return base_url

# E.g: Given the viewset PersonViewSet that manages people gen a URL to filter only cubans
# That is when the function becomes handy
# /api/v1/people?country=Cuba

# reverse(
#     view_name='person-list#v1',
#     query_kwargs={"country": "Cuba"},
#     request=request,
# )