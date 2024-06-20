# Dauto

Solutions for commons issues on django projects

## Description

This project is a collection of common solutions for Django projects. It aims to assist developers who are working with
Django by providing tried-and-tested solutions to recurring issues and challenges. The strategies covered in this
project span from basic to advanced topics, making it a versatile resource for both beginners and experienced Django
developers. It facilitates quick problem-solving in Django projects and significantly reduces development time and
effort. With these solutions at hand, developers can focus more on other crucial aspects of their projects.

## Use Cases

We think that cover from simple to complex can be useful in the module learning curve so... let's go 🚀!!!

### Using classes dynamically

Asume tha we have a file in 'module/test.py' with the next code on it:

```python
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



