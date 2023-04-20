from .utils import extend_model
from libs.utils.decorators import staticproperty

# from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.automap import automap_base, AutomapBase
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from typing import Any, Callable, List
import uuid


class SQLAlchemyStructuredProvider:
    @staticproperty
    def SUPPORTED_SCHEMES(self) -> list:
        return ["sql"]

    @staticproperty
    def DEFAULT_SCHEMA(self) -> str:
        return "default"

    @property
    def SCHEMA(self) -> dict:
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

    def __init__(self, *args, **kwargs) -> None:
        kw = kwargs.keys()
        kwargs.pop("scheme")
        self.id: str = uuid.uuid4().hex
        self.schemas: List[str] = (
            kwargs.pop("schemas")
            if "schemas" in kw
            else [kwargs.pop("schema")]
            if "schema" in kw
            else []
        )
        self.engine: Engine = (
            kwargs.pop("engine")
            if "engine" in kw
            else create_engine(kwargs.pop("url"), **kwargs)
            if "url" in kw
            else None
        )
        if not self.engine:
            raise Exception("No engine configuration values specified.")

        self.base: AutomapBase = automap_base()
        self.session: Callable = lambda: Session(self.engine)

        for schema in self.schemas:
            self.base.prepare(
                autoload_with=self.engine,
                schema=schema,
                modulename_for_table=self.modulename_for_table,
            )
        self.models = self.base.by_module.get(self.id)
        for schema in self.models.keys():
            for model in self.models[schema].keys():
                extend_model(model=self.models[schema][model], session=self.session)

    def __getitem__(self, handle):
        return self.models[handle]

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
                table = self[schema][table_name]
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
                table = self[schema][table_name]
        value = session.query(table).get(key)
        if value:
            value = value.__dict__
            value.pop("_sa_instance_state")
        return value

    def filter(
        self, filters: List[str], decoder: Callable = None, **kwargs
    ) -> List[Any]:
        pass

    def drop(
        self, key: str, table_name: str = None, schema: str = None, table=None
    ) -> None:
        session = self.session()
        if not table:
            if not table_name and not schema:
                table, key = self.parse_key(key)
            if table_name and not schema:
                table = self[self.DEFAULT_SCHEMA][table_name]
        session.delete(session.query(table).get(key))
        session.commit()

    def parse_key(self, key: str) -> Any:
        key = key.split(".")
        schema, table_name = key[0:2]
        key = ".".join(key[2:])
        return self[schema][table_name], key

    def modulename_for_table(self, cls, tablename, table) -> str:
        return (
            f"{self.id}.{table.schema}"
            if getattr(table, "schema", None)
            else f"{self.id}.{self.DEFAULT_SCHEMA}"
        )
