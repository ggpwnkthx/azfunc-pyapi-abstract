from libs.utils.decorators import staticproperty
from typing import Any, Callable, List
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session


class SQLAlchemyStorageProvider:
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> list:
        return ["sql"]

    @staticproperty
    def DEFAULT_SCHEMA(self) -> str:
        return self.DEFAULT_SCHEMA

    @property
    def SCHEMA(self) -> list:
        return {
            name: {
                "fields": {
                    field.key: {
                        "type": field.type.__visit_name__,
                        "readOnly": getattr(
                            field,
                            "primary_key",
                            getattr(
                                field,
                                "__read_only__",
                                getattr(table, "__read_only__", False),
                            ),
                        ),
                    }
                    for field in inspect(table).columns
                },
                "relationships": {
                    relationship.name: {
                        "type": getattr(
                            relationship.class_,
                            "__name__",
                            getattr(relationship.class_, "__collection_name__", None),
                        ),
                        "to": "many" if hasattr(relationship, "uselist") else "one",
                    }
                    for relationship in getattr(inspect(table), "relationships", [])
                },
            }
            for name, table in self.base.metadata.tables.items()
        }

    def prefix_tablename_with_schema(self, cls, tablename, table):
        if table.schema is not None:
            return table.schema
        else:
            return self.DEFAULT_SCHEMA

    def __init__(self, *args, **kwargs) -> None:
        if len(args):
            self.scheme = args[0]
        if "scheme" in kwargs:
            self.scheme = kwargs.pop("scheme")

        if "schemas" in kwargs:
            self.schemas = kwargs.pop("schemas")
        else:
            self.schemas = []
        if "url" in kwargs:
            self.engine = create_engine(kwargs.pop("url"), **kwargs)
        elif "engine" in kwargs:
            self.engine = kwargs.pop("engine")
        else:
            raise Exception("No engine configuration values specified.")
        self.base = automap_base()
        if len(self.schemas):
            for schema in self.schemas:
                self.base.prepare(
                    self.engine,
                    schema=schema,
                    modulename_for_table=self.prefix_tablename_with_schema,
                )
        else:
            self.base.prepare(
                self.engine, modulename_for_table=self.prefix_tablename_with_schema
            )

        self.session = lambda: Session(self.engine)
    
    def connect(self) -> Session:
        return self.session()

    def save(
        self,
        key: str,
        value: dict,
        table_name: str = None,
        schema: str = None,
        table=None,
    ) -> None:
        session = self.session()
        if not table:
            if not table_name and not schema:
                table, key = self.parse_key(key)
            if table_name and not schema:
                table = self.get_table(name=table_name, schema=schema)
        record = session.query(table).get(key)
        if record:
            for k, v in value.items():
                setattr(record, k, v)
        else:
            session.add(table(**value))
        session.commit()

    def load(
        self, key: str, table_name: str = None, schema: str = None, table=None
    ) -> Any:
        session = self.session()
        if not table:
            if not table_name and not schema:
                table, key = self.parse_key(key)
            if table_name and not schema:
                table = self.get_table(name=table_name, schema=schema)
        value = session.query(table).get(key).__dict__
        value.pop('_sa_instance_state')
        return value

    def filter(
        self, filters: List[str], decoder: Callable = None, **kwargs
    ) -> List[Any]:
        pass

    def drop(self, key: str, table_name: str = None, schema: str = None, table=None
    ) -> None:
        session = self.session()
        if not table:
            if not table_name and not schema:
                table, key = self.parse_key(key)
            if table_name and not schema:
                table = self.get_table(name=table_name, schema=schema)
        session.delete(session.query(table).get(key))
        session.commit()
    
    def get_table(self, name: str, schema: str = None):
        return getattr(
            getattr(
                self.base.by_module,
                schema or self.DEFAULT_SCHEMA,
                None,
            ),
            name,
            None,
        )

    def parse_key(self, key: str):
        key = key.split(".")
        schema, table_name = key[0:2]
        key = ".".join(key[2:])
        return self.get_table(name=table_name, schema=schema), key

