from libs.data import register_binding
import os

# OneView Tasks
register_binding(
    "roku",
    "Structured",
    "sql",
    url=os.environ["DATABIND_SQL_ROKU"],
    schemas=["dbo"],
)