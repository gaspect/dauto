# # Database

import urllib.parse as urlparse

# When we deploy Django projects usually we get the database url as a configuration **string** so it's tricky
# destructure that configuration string in a proper database configuration for django. This module try to
# cover that for you.

# We start registering database common schemes in URLs like objects.

urlparse.uses_netloc.append("postgres")
urlparse.uses_netloc.append("mysql")
urlparse.uses_netloc.append("sqlite")

# Then we do a mapping of most used (a very opinionated stuff, We know) django database backends

SCHEMES = {
    "postgres": "django.db.backends.postgresql",
    "mysql": "mysql.connector.django",
    "sqlite": "django.db.backends.sqlite3",
}


# Then we build the magic method that with a very few parameters alongside the url configuration return
# a valid django configuration for databases.

def database(url, engine=None, conn_max_age=0, conn_health_checks=False, **options):
    """
    The `database` method is used to parse a database URL and return a configuration dictionary for connecting to the database.

    Parameters:
         url (string): The URL of the database to connect to.
         engine (string, optional): The database engine to use. Defaults to `None`.
         conn_max_age (int, optional): The maximum age of database connections in seconds. Defaults to `0`.
         conn_health_checks (bool, optional): Indicates whether to perform health checks on database connections. Defaults to `False`.
         **options (dict, optional): Additional database connection options. These will be added to the configuration dictionary.

    Returns:
        config (dict): The configuration dictionary for connecting to the database.
    """

    if url == "sqlite://:memory:":
        # this is a special case, because if we pass this URL into
        # urlparse, urlparse will choke trying to interpret "memory"
        # as a port number
        return {"ENGINE": SCHEMES["sqlite"], "NAME": ":memory:"}
        # note: no other settings are required for sqlite

    # otherwise parse the url as normal
    config = {}

    url = urlparse.urlparse(url)

    # Split query strings from path.
    path = url.path[1:]
    if "?" in path and not url.query:
        path, query = path.split("?", 2)
    else:
        path, query = path, url.query
    query = urlparse.parse_qs(query)

    # If we are using sqlite, and we have no path, then assume we
    # want an in-memory database (this is the behaviour of sqlalchemy)
    if url.scheme == "sqlite" and path == "":
        path = ":memory:"

    # Handle postgres percent-encoded paths.
    hostname = url.hostname or ""
    if "%2f" in hostname.lower():
        # Switch to url.netloc to avoid lower cased paths
        hostname = url.netloc
        if "@" in hostname:
            hostname = hostname.rsplit("@", 1)[1]
        if ":" in hostname:
            hostname = hostname.split(":", 1)[0]
        hostname = hostname.replace("%2f", "/").replace("%2F", "/")

    # Lookup specified engine.
    engine = SCHEMES[url.scheme] if engine is None else engine

    port = url.port

    # Update with environment configuration.
    config.update(
        {
            "NAME": urlparse.unquote(path or ""),
            "USER": urlparse.unquote(url.username or ""),
            "PASSWORD": urlparse.unquote(url.password or ""),
            "HOST": hostname,
            "PORT": port or "",
            "CONN_MAX_AGE": conn_max_age,
            "CONN_HEALTH_CHECKS": conn_health_checks
        }
    )

    for key, values in query.items():
        if url.scheme == "mysql" and key == "ssl-ca":
            options["ssl"] = {"ca": values[-1]}
            continue

        options[key] = values[-1]

    # Support for Postgres Schema URLs
    if "currentSchema" in options and engine == "django.db.backends.postgresql":
        options["options"] = "-c search_path={0}".format(options.pop("currentSchema"))

    if options:
        config["OPTIONS"] = options

    if engine:
        config["ENGINE"] = engine

    return config
