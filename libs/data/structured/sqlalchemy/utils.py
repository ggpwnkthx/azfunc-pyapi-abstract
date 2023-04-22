from typing import Any, Callable, Union
import re
import inflect


def camelize_classname(base, tablename, table):
    "Produce a 'camelized' class name, e.g."
    "'words_and_underscores' -> 'WordsAndUnderscores'"
    schema = table.schema.replace(" ", "_")
    schema = str(
        schema[0].upper()
        + re.sub(r"_([a-z])", lambda m: m.group(1).upper(), schema[1:])
    )
    tablename = tablename.replace(" ", "_")
    tablename = str(
        tablename[0].upper()
        + re.sub(r"_([a-z])", lambda m: m.group(1).upper(), tablename[1:])
    )
    return schema + tablename


_pluralizer = inflect.engine()


def pluralize_collection(base, local_cls, referred_cls, constraint):
    "Produce an 'uncamelized', 'pluralized' class name, e.g."
    "'SomeTerm' -> 'some_terms'"

    referred_name = referred_cls.__name__
    uncamelized = re.sub(r"[A-Z]", lambda m: "_%s" % m.group(0).lower(), referred_name)[
        1:
    ]
    pluralized = _pluralizer.plural(uncamelized)
    return pluralized


from sqlalchemy.orm import Session
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import simplejson


def extend_model(model: Any, session: Session) -> None:
    setattr(model, "__class_getitem__", model_get(session))
    setattr(model, "__getitem__", lambda self, key: getattr(self, key))
    setattr(model, "__setitem__", model_set_column)
    setattr(
        model,
        "__marshmallow__",
        type(
            f"{model.__name__}Schema",
            (SQLAlchemyAutoSchema,),
            {
                "Meta": type(
                    "Meta",
                    (object,),
                    {
                        "model": model,
                        "sqla_session": session,
                        "render_module": simplejson,
                        # "include_relationships": True,
                        # "load_instance": True,
                    },
                )
            },
        ),
    )
    setattr(model, "__repr__", lambda self: self.__marshmallow__().dumps(self))


def model_set_column(self: object, key: str, value: Any) -> None:
    setattr(self, key, value)
    self._sa_instance_state.session.commit()


import logging
from sqlalchemy import Column
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Mapper, Query, InstrumentedAttribute
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList


class QueryFrame:
    def __init__(self, model: Any, session: Session) -> None:
        self.model = model
        self.mapper: Mapper = inspect(model)
        self.session = session
        self.select = []
        self.ops = []
        self.sort = []
        self.limit = 0
        self.offset = 0

    @property
    def __primary_key__(self) -> Column:
        for column in self.mapper.columns.values():
            if column.primary_key:
                return column

    def __getitem__(self, key: Any = None):
        match key:
            case list():
                logging.debug(("list", type(key), key))
                for item in key:
                    self[item]
            case tuple():
                logging.debug(("tuple", type(key), key))
                return [self[item] for item in key]
            case InstrumentedAttribute():
                logging.debug(("column", type(key), key))
                self.select.append(key)
            case BinaryExpression() | BooleanClauseList():
                logging.debug(("expression", type(key), key))
                self.ops.append(("where", key))
            case str():
                logging.debug(("string", type(key), key))
                return self.__getitem_field(key)
            case slice():
                logging.debug(("slice", type(key), key))
                self.limit = key.stop - key.start
                self.offset = key.start
            case _:
                logging.debug(("other", type(key), key))
        return self

    def __build__(self) -> Query:
        query: Query = (
            self.session().query(*(self.select or [self.model])).select_from(self.model)
        )
        for op in self.ops:
            query = getattr(query, op[0])(op[1])
        return query

    def __call__(self):
        return self.__build__().all()
    
    def __len__(self) -> int:
        return self.__build__().count()

    def __repr__(self) -> str:
        try:
            from sql_formatter.core import format_sql
            return format_sql(str(self.__build__()))
        except:
            return str(self.__build__())

    def __getitem_id(Self, key):
        logging.warn(("id", type(key), key))

    def __getitem_field(self, key):
        if isinstance(field := getattr(self.model, key, None), InstrumentedAttribute):
            return field
    
    def to_pandas(self):
        try:
            import pandas as pd
        except:
            raise Exception("Pandas is not installed.")
        return pd.read_sql(str(self.__build__()), self.session().connection())


def model_get(session: Session) -> Callable:
    @classmethod
    def __class_getitem__(cls, key) -> Union[Query, Any]:
        frame = QueryFrame(cls, session)
        return frame[key]

    return __class_getitem__
