# # Django Rest Framework

# Now more than ever APIS are fashionable with microservices, lambdas, serverless functions etc, and the
# framework (all least one of then ) for make APIS using Django is the Django Rest Framework. Thi section
# cover a sets of class extensions to this framework to solve common issues.

# ??? warning
#
# We need to check if djangorestframework package is installed


try:
    import rest_framework
except ImportError as e:
    raise ImportError("You must install dauto[rest] packages to use this package.")
