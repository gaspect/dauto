import typing
from django.db.models import deletion
from contextlib import contextmanager
from .utils.using import using

try:
    from rest_polymorphic.serializers import PolymorphicSerializer
    from polymorphic.models import PolymorphicModel
except ImportError as e:
    raise ImportError("You must install 'django-rest-polymorphic' or dauto[polymorphic] packages to use this package.")


# noinspection SpellCheckingInspection
def polymorphic(model, *_serializers, resourcetype_name="resourcetype"):
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
