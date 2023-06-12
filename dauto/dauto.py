import urllib.parse as urlparse

# Register database schemes in URLs.
urlparse.uses_netloc.append("postgres")
urlparse.uses_netloc.append("mysql")
urlparse.uses_netloc.append("sqlite")


SCHEMES = {
    "postgres": "django.db.backends.postgresql",
    "mysql": "mysql.connector.django",
    "sqlite": "django.db.backends.sqlite3",
}


def database(url, engine=None, conn_max_age=0, **options):
    """Parses a database URL."""

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