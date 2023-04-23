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


from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import Session, Query
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


from .interface import QueryFrame


def model_get(session: Session) -> Callable:
    @classmethod
    def __class_getitem__(cls, key) -> Union[Query, Any]:
        frame = QueryFrame(cls, session)
        return frame[key]

    return __class_getitem__
