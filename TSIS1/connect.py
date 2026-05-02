import psycopg2
from config import host, user, password, db_name


def get_connection() -> psycopg2.extensions.connection:
    """Return an autocommit psycopg2 connection."""
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        options="-c client_encoding=UTF8",
    )
    conn.autocommit = True
    return conn
