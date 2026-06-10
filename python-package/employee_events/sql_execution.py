from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Using pathlib, create a `db_path` variable
# that points to the absolute path for the `employee_events.db` file
db_path = Path(__file__).resolve().parent / "employee_events.db"


# Helper functions for explicit connection management
def open_connection(path: Path = db_path):
    """
    Open and return a sqlite3 connection to the given database path.
    """
    return connect(path)


def execute_query(sql_query: str, params=None, connection=None, fetchone: bool = False, as_dataframe: bool = False):
    """
    Execute `sql_query` using a provided connection or a new connection.

    - If `as_dataframe` is True, returns a pandas DataFrame.
    - If `fetchone` is True, returns a single row tuple (or None).
    - Otherwise returns a list of tuples.

    The connection is closed only if this function opened it.
    """
    close_conn = False
    if connection is None:
        connection = connect(db_path)
        close_conn = True
    try:
        if as_dataframe:
            return pd.read_sql_query(sql_query, connection, params=params)
        cursor = connection.cursor()
        if params is None:
            cursor.execute(sql_query)
        else:
            cursor.execute(sql_query, params)
        return cursor.fetchone() if fetchone else cursor.fetchall()
    finally:
        if close_conn:
            connection.close()


def close_connection(connection):
    """
    Close the given sqlite3 connection if it is open. Silently ignores errors.
    """
    try:
        connection.close()
    except Exception:
        pass


# OPTION 1: MIXIN
# Define a class called `QueryMixin`
class QueryMixin:

    # Define a method named `pandas_query`
    # that receives an sql query as a string
    # and returns the query's result
    # as a pandas dataframe
    def pandas_query(self, sql_query: str, params=None) -> pd.DataFrame:
        """
        Execute `sql_query` against the packaged employee_events.db and
        return the result as a pandas DataFrame. The database connection
        is closed before returning.
        """
        connection = connect(db_path)
        try:
            df = pd.read_sql_query(sql_query, connection, params=params)
            return df
        finally:
            connection.close()

    # Define a method named `query`
    # that receives an sql_query as a string
    # and returns the query's result as
    # a list of tuples. (You will need
    # to use an sqlite3 cursor)
    def query(self, sql_query: str, params=None):
        """
        Execute `sql_query` and return the result as a list of tuples.
        The database connection is closed before returning.
        """
        connection = connect(db_path)
        try:
            cursor = connection.cursor()
            if params is None:
                result = cursor.execute(sql_query).fetchall()
            else:
                result = cursor.execute(sql_query, params).fetchall()
            return result
        finally:
            connection.close()


# Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query
