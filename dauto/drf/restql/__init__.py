try:
    import django_restql
except ImportError as e:
    raise ImportError("You must install dauto[django-restql] packages to use this package.")