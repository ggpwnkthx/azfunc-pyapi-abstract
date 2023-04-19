from .schema import camelize_classname, pluralize_collection
from libs.utils.decorators import staticproperty
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.automap import automap_base, AutomapBase
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from typing import Any, Callable, List
import uuid

from libs.utils.logger import get as Logger

logger = Logger("SQLAlchemyStructuredProvider")


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

    def modulename_for_table(self, cls, tablename, table) -> str:
        return (
            f"{self.id}.{table.schema}"
            if getattr(table, "schema", None)
            else f"{self.id}.{self.DEFAULT_SCHEMA}"
        )

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
                # classname_for_table=camelize_classname,
                # name_for_collection_relationship=pluralize_collection,
                modulename_for_table=self.modulename_for_table,
            )
        # for engine in self.base.by_module.keys():
        #     for schema in self.base.by_module[engine].keys():
        #         for model in self.base.by_module[engine][schema].keys():
        #             setattr(
        #                 self.base.by_module[engine][schema][model],
        #                 "__marshmallow__",
        #                 type(
        #                     self.base.by_module[engine][schema][model].__name__ + "Schema",
        #                     (SQLAlchemyAutoSchema,),
        #                     {
        #                         "Meta": type(
        #                             "Meta",
        #                             (object,),
        #                             {
        #                                 "model": self.base.by_module[engine][schema][model],
        #                             },
        #                         )
        #                     },
        #                 ),
        #             )
        self.models = self.base.by_module.get(self.id)

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
                table = self.get_model(name=table_name, schema=schema)
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
                table = self.get_model(name=table_name, schema=schema)
        value = session.query(table).get(key).__dict__
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
                table = self.get_model(name=table_name, schema=schema)
        session.delete(session.query(table).get(key))
        session.commit()

    def get_model(self, name: str, schema: str = None) -> Any:
        return getattr(
            getattr(
                getattr(
                    self.base.by_module,
                    self.id,
                    None,
                ),
                schema or self.DEFAULT_SCHEMA,
                None,
            ),
            name,
            None,
        )

    def parse_key(self, key: str) -> Any:
        key = key.split(".")
        schema, table_name = key[0:2]
        key = ".".join(key[2:])
        return self.get_model(name=table_name, schema=schema), key
