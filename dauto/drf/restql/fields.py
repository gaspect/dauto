# ??? warning
#
# We need to check if django_restql package is installed
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django_restql.mixins import DynamicFieldsMixin

from dauto.drf.reverse import URLConfig, reverse

from django_restql.fields import DynamicSerializerMethodField
from django_restql.parser import Query
from typing import Type
from rest_framework.serializers import Serializer

# Addressing Over-fetching and Under-fetching in RESTful APIs
# RESTful APIs often suffer from over-fetching and under-fetching issues due to their rigid approach to handling response payloads.
# These problems arise because REST endpoints return fixed sets of fields, which may include unnecessary data (over-fetching) or lack required data (under-fetching), forcing clients to make additional requests.

# At its core, this is a design problem, as traditional REST APIs do not offer granular control over the response structure.
# One effective way to tackle this issue in Django REST Framework (DRF) is by using the
# [Django RESTQL](https://yezyilomo.github.io/django-restql/). This library transforms Django REST Framework (DRF) APIs into GraphQL-like APIs, enabling clients to specify the exact fields they need in a query-like format.

# However, while this approach provides flexibility, it also encourages resource nesting, an opinionated practice that is often criticized from a design standpoint. Deeply nested structures can disrupt HATEOAS (Hypermedia as the Engine of Application State), a key principle in RESTful API design. HATEOAS advocates for hypertext-driven APIs, where resources are interconnected through hyperlinks rather than deeply nested objects.
# First time you hear about this concept? We recommend you to read about it in:
# - [REST APIs must be hypertext-driven » Untangled](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven)
# - [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)

# In essence, HATEOAS emphasizes that REST APIs should expose relationships between resources via hyperlinks rather than embedding them directly. Django REST Framework acknowledges this principle through the [HyperlinkedModelSerializer](https://www.django-rest-framework.org/api-guide/serializers/#hyperlinkedmodelserializer), which encourages hyperlinking resources rather than nesting them.
# So, how can we leverage both mechanisms without compromising API design?

# We need a solution that balances the flexibility of Django RESTQL while preserving HATEOAS principles. The HyperlinkedNestedSerializerMethodField is designed to achieve exactly that—allowing APIs to provide both hypermedia-driven links and selectively nested representations based on client queries.

class HyperlinkedNestedSerializerMethodField(DynamicSerializerMethodField):
    """
    A specialized field that integrates HATEOAS (Hypermedia as the Engine of Application State)
    with nested resource serialization in a single field.

    This field allows:
    - Dynamically generating hyperlinked URLs for related resources.
    - Serializing nested resources when query arguments specify field inclusion or exclusion.

    Behavior:
    - If query parameters request specific nested fields, the related resource(s) will be serialized
      using the provided `serializer_class`, respecting the parsed query structure.
    - Otherwise, the field will return a hyperlink to the related resource, constructed using
      a method defined on the parent serializer.

    Parameters:
        serializer_class (Type[Serializer]): The serializer class to use for nested resource serialization.
        source (str, optional): The source attribute from which the field retrieves data. Defaults to `None`,
            which assigns it to the field name.
        many (bool, optional): Whether the field should handle multiple related instances. Defaults to `False`.
        method_name (str): The name of the method on the parent serializer responsible for
            providing the URL configuration. By default, is resolved with get_<field_name>

    Raises:
        ImproperlyConfigured: If the method specified in `method_name` does not return an instance of `URLConfig`.

    Example:
        class ExampleSerializer(serializers.Serializer):
            related_resource = HyperlinkedNestedSerializerMethodField(
                serializer_class=NestedResourceSerializer,
                method_name="get_related_resource_url"
            )

            def get_related_resource_url(self, instance, parsed_query):
                return URLConfig(
                    view_name="related-resource-detail",
                    path_params={"pk": instance.related.id},
                )
    """

    # noinspection PyTypeChecker
    def __init__(
            self,
            serializer_class: Type[Serializer],
            source: str = None,
            many: bool = False,
            method_name: str = None,
            **kwargs,
    ):
        super().__init__(method_name=method_name, **kwargs)

        self.serializer_class = serializer_class
        self.source = source or self.field_name
        self.many = many

    # noinspection PyTypeChecker,PyCallingNonCallable,PyUnresolvedReferences
    def to_representation(self, value):
        is_parsed_query_available = (
                hasattr(self.parent, "restql_nested_parsed_queries")
                and self.field_name in self.parent.restql_nested_parsed_queries
        )

        if is_parsed_query_available:
            parsed_query = self.parent.restql_nested_parsed_queries[self.field_name]
        else:
            parsed_query = Query(
                field_name=None,
                included_fields=["*"],
                excluded_fields=[],
                aliases={},
                arguments={},
            )

        has_fields = (
                parsed_query.included_fields
                and "*" not in parsed_query.included_fields
                or parsed_query.excluded_fields
                or parsed_query.aliases
        )

        if has_fields:
            if issubclass(self.serializer_class, DynamicFieldsMixin):
                return self.serializer_class(
                    instance=value,
                    context=self.context,
                    parsed_query=parsed_query,
                    many=self.many,
                ).data
            else:
                return self.serializer_class(
                    instance=value,
                    context=self.context,
                    many=self.many,
                ).data


        if not isinstance(value, Model):
            value = self.parent.instance

        url_config = self._get_url_config(value, parsed_query)
        return self.reverse_url(url_config)

    def reverse_url(self, url_config: URLConfig):
        return reverse(
            view_name=url_config.view_name,
            kwargs=url_config.path_params,
            query_kwargs=url_config.query_params,
            request=self.parent.context.get("request"),
        )

    def _get_url_config(self, instance, parsed_query):
        method = getattr(self.parent, self.method_name)
        url_config = method(instance, parsed_query)
        if not isinstance(url_config, URLConfig):
            raise ImproperlyConfigured(
                f"Method {self.method_name} in {self.parent.__class__.__name__} must return an {URLConfig.__name__} instance, its returning {url_config.__class__.__name__}"
            )

        return url_config
