# # Polymorphic

import typing
from django.db.models import deletion, Model
from contextlib import contextmanager
from ._utils.using import using


def polymorphic(model: Model, *_serializers: str, resourcetype_name="resourcetype"):
    """
      Create a polymorphic serializer using already defined serializers over the related models

      Parameters:
          model: The parent model
          *_serializers: List of serializers to use
          resourcetype_name: The name of the resource type in the resulting polymorphic serializer
      """

    # ??? warning
    #
    # We need to check if polymorphic packages are installed

    try:
        from rest_polymorphic.serializers import PolymorphicSerializer
    except ImportError as e:
        raise ImportError("You must install dauto[polymorphic-rest] package to use this package.")

    final_klass_name = f"{model.__class__.__name__}PolymorphicSerializer"
    classes = [using(s) for s in _serializers]
    return type(
        final_klass_name,
        (PolymorphicSerializer,),
        {
            "resource_type_field_name": resourcetype_name,
            "model_serializer_mapping": {
                k.Meta.model: k for k in classes  # type: ignore
            },
        },
    )


@contextmanager
def collector(klass: typing.Type[deletion.Collector]):
    """
    This method monkey patch the collect method in an admin class in certain context to use
    polymorphic complaints operations over the related models
    """

    # ??? warning
    #
    # We need to check if polymorphic packages are installed

    try:
        from polymorphic.models import PolymorphicModel
    except ImportError as e:
        raise ImportError("You must install dauto[polymorphic-model] package to use this package.")

    original = getattr(klass, "collect")

    def custom(self, objs, source=None, source_attr=None, **kwargs):
        if len(objs) > 0 and isinstance(objs[0], PolymorphicModel):
            for o in objs:
                original(self, [o], source=None, source_attr=None, **kwargs)
        else:
            original(self, objs, source=None, source_attr=None, **kwargs)

    klass.collect = custom
    yield
    klass.collect = original
