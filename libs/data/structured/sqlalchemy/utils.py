from sqlalchemy.orm import Session, Query
from sqlalchemy.schema import ForeignKeyConstraint
from typing import Any, Callable, List, Union, Type

EXTENSION_STEPS: List[Callable] = [
    lambda model, session: setattr(model, "__class_getitem__", model_get(session)),
    lambda model, _: setattr(
        model, "__getitem__", lambda self, key: getattr(self, key)
    ),
    lambda model, _: setattr(model, "__setitem__", model_set_column),
]


def extend_models(models: List[Any], session: Session) -> None:
    for func in EXTENSION_STEPS:
        for model in models:
            func(model, session)


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

import logging

def name_for_collection_relationship(
    base: Type[Any],
    local_cls: Type[Any],
    referred_cls: Type[Any],
    constraint: ForeignKeyConstraint,
):
    # if len(constraint.column_keys) == 1:
    #     if constraint.column_keys[0][-3:] == "_id":
    #         return f'related_{constraint.column_keys[0][:-3].lower()}'
    if constraint.comment:
        return f'{constraint.comment.lower()}'
    if constraint.name:
        return f'{constraint.name.lower()}'
