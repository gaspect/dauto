# Dauto

Solutions for commons issues on Django and drf projects

## Description

This project is a collection of common solutions for Django projects. It aims to assist developers who are working with
Django by providing tried-and-tested solutions to recurring issues and challenges. The strategies covered in this
project span from basic to advanced topics, making it a versatile resource for both beginners and experienced Django
developers. It facilitates quick problem-solving in Django projects and significantly reduces development time and
effort. With these solutions at hand, developers can focus more on other crucial aspects of their projects. To learn more
read the [documentation](https://gaspect.github.io/dauto/).

## Use Cases

We think that cover from simple to complex can be useful in the module learning curve so... let's go 🚀!!!

### Using classes dynamically

Asume tha we have a file in 'module/test.py' with the next code on it:

```python
# module/test.py
class TestClass:
    ...
```

Now we need to be dynamically capable to create instances of `TestClass` without import directive.
The `using` function inside `utils` can do the hard job for us.

```python
from dauto.utils import using

TestClass = using("module.main.TestClass")

# Now we have a TestClass type, lets create a TestClass instance

instance = TestClass()

# done !!!
```

### Make functions awaitable

For some reason we need turn a normal function into an `async` function then we can use the 
`awaitable` decorator inside `utils`

```python
from dauto.utils import awaitable
import  asyncio

@awaitable
def test_function():
    print("Hello world")


asyncio.run(test_function()) # This work even without `async` syntax
```
### Build singletons

Singletons are a common design pattern, a detail explanation can be found [here](https://refactoring.guru/design-patterns/singleton). 
The `singleton` function inside `utils` is our python implementation of that design pattern.

```python
from dauto.utils import singleton

@singleton
class Omniscient:
    ...


a = Omniscient()
b = Omniscient()

print(a is b) # Output: True
```


### Configure django databases based on urls

```python
from dauto.database import  database
import os
DATABASES = {
    "default": database(os.getenv("DATABASE_URL"), conn_max_age=None, conn_health_checks=True),
    "test": {
        "NAME": "test.sqlite3",
        "ENGINE": "django.db.backends.sqlite3",
    },
}
```
### Embed admin definitions in models

We can do it this way 

```python
# app/model.py
from django.db import  models
from django.contrib import admin


class Poll(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    class Admin(admin.ModelAdmin):
        list_display = ["title", "active"]
        search_fields = ["title"]
```

then on application config do

```python
from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps"

    def ready(self) -> None:
        from dauto.admin import register # 👈
        from app import  models # 👈
        
        register(models) # 👈
```


### Avoid circular signal call

This happens when two signals call each other, how break the cicle can be tricky we do it for you

```python
from django.db import models
from django.db.models import signals
from django.dispatch import receiver

from dauto.signals import OutSignal

class A(models.Model):
    ...

class B(models.Model):
    a = models.ManyToManyField(A)

@receiver(signals.post_save, sender=A)
def on_a_change(sender, instance, **kwargs):
    for b in  instance.b_set.all():
        b.update(**{})
    
@receiver(signals.post_save, sender=B)
def on_b_change(sender, instance, **kwargs):
    with OutSignal(signals.post_save, on_a_change, A ): # 👈 disconnect on_a_change for this code block
        for a in  instance.a.all():
            a.update(**{})
```

### Model permission for DRF function base views

```python
from rest_framework import decorators
from app.models import  SomeModel # 👈 Asume this exist
from dauto.drf.permission import permissions_for

@decorators.api_view(["GET", "POST"])
@decorators.permission_classes(permissions_for(SomeModel))
def some_model_view(request):
    ...
```

### Custom namespace versioning

```python
# common/versioning.py

from dauto.drf.versioning import CustomNamespaceVersioning

class SharpNamespaceVersioning(CustomNamespaceVersioning):
    separator = "#"
```

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "common.versioning.SharpNamespaceVersioning",
}
```

Now your views can be reversed using `someview-details#v1`

### Custom serializers getters for generic viewsets

Can be used to retrieve serializers based on operations

```python
from dauto.drf.viewsets.mixin import ByOperationSerializerMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework import decorators
from app.serializers import AReadSerializer, AWriteSerializer, CustomOppSerializer

class AViewSet(ByOperationSerializerMixin, ModelViewSet):
    
    @decorators.action(["POST"], detail=True)
    def custom_opp(self, request): # will user serialize with key `custom_app` and fallback to 'write' key serializer 
        # if not found because is a 'POST' an operation that write on the DB
        ...
    
    serializer_class = {
        "read": AReadSerializer,
        "write": AWriteSerializer,
        "custom_opp": CustomOppSerializer
    }
```
or retrieve serializers based on versions

```python
from dauto.drf.viewsets.mixin import ByVersionSerializerMixin
from rest_framework.viewsets import ModelViewSet
from app.serializers import AReadSerializerV1, AWriteSerializerV2

class AViewSet(ByVersionSerializerMixin, ModelViewSet):
    
    serializer_class = {
        "v1": AReadSerializerV1,
        "v2": AWriteSerializerV2,
    }
```

Then the `AViewSet` class can be used in two separated versions (namespace, url, whatever) and use different serializers for any of these version
keeping the logic without change.

We can use combinations of both for different effects


```python
from dauto.drf.viewsets.mixin import ByVersionSerializerMixin, ByOperationSerializerMixin
from rest_framework.viewsets import ModelViewSet
from app import serializers

class AViewSet(ByOperationSerializerMixin, ByVersionSerializerMixin, ModelViewSet):
    
    serializer_class = {
        "v1": {
            "read": serializers.v1.AReadSerializer,
            "write": serializers.v1.AWriteSerializer
        },
        "v2": {
            "read": serializers.v2.AReadSerializer,
            "write": serializers.v2.AWriteSerializer
        },
    }
```
### Verbose creation and update methods

When we say verbose we refer to use a read serializer like to process the instance created. This make
good combination with serializer getters

```python

from dauto.drf.viewsets.mixin import ByVersionSerializerMixin, ByOperationSerializerMixin
from dauto.drf.viewsets.mixin import CreateVerboseModelMixin, UpdateVerboseModelMixin

from rest_framework.viewsets import  GenericViewSet
from rest_framework import mixins
from app import serializers

class AViewSet(
    CreateVerboseModelMixin, # 👈
    mixins.RetrieveModelMixin,
    UpdateVerboseModelMixin, # 👈
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    ByOperationSerializerMixin, # 👈
    ByVersionSerializerMixin, # 👈
    GenericViewSet
):
    
    serializer_class = {
        "v1": {
            "read": serializers.v1.AReadSerializer,
            "write": serializers.v1.AWriteSerializer
        },
        "v2": {
            "read": serializers.v2.AReadSerializer,
            "write": serializers.v2.AWriteSerializer
        },
    }
```

Even if you use your own serializer system to get a writer and read serializer it will work, and
use the serializer defined to be obtained in a read method as the verbose one.

### Event Buss and event handling

We achieve this using an observer pattern and some copy/paste from already knows pub-subs systems like
RabitMQ or Kafka. We start creating the bus

```python
from dauto.utils.events import EventBus

eb = EventBus()
```
Then defina a handler for certain topic. A topic is blob pattern representing, what we are gone to
listen, these pattern are formed by namespaces splits by dots (`.`) and  asterisks (`*`) as
namespace wildcard. So the namespace `test.*` can hear from `test.creation`, `test.deletion`, etc ...
let's see some examples.

```python

from dauto.utils.events import EventBus, Event

eb = EventBus()

@eb.subscribe("test.*") # we suscribe to all test derived but not for only test
def test_derived_handler(e:Event):
    print(e)

@eb.subscribe("test.*.data") # only subscribes for test derived that derive in data
async def test_derived_data_handler(e:Event): # 🤓 check this, is async but work
    print(e)
```

now we can dispatch an event using the bus

```python
eb.dispatch(Event(
    topic="test.test",
    payload="Hola mundo test.test"
))
eb.dispatch(Event(
    topic="test.whatever.data",
    payload="Hola mundo test.whatever.data"
))
eb.dispatch(Event(
    topic="test.anotherone.data",
    payload="Hola mundo test.anotherone.data"
))
```

The first dispatch  with topic `test.test` will be handled by `test_derived_handler` the other two
with topics `test.whatever.data` and `test.anotherone.data` will be handled by `test_derived_data_handler`.
Beside the topic version can be used to additional matching

```python
from dauto.utils.events import EventBus, Event

eb = EventBus()

@eb.subscribe("test.*", version="0.0.1") # only will match if topic and version match
def test_derived_handler_with_version(e:Event):
    print(e)

# this will not match
eb.dispatch(Event(
    topic="test.mismatch_version",
    payload="Test payload",
    version="0.0.2"
)) 

# this will  match
eb.dispatch(Event(
    topic="test.right_version",
    payload="Test payload",
    version="0.0.1"
))
```

> I think this cover all the project, happy coding ️ ☺️👋