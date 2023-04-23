from sqlalchemy import Column
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import InstrumentedAttribute, Mapper, Query, Session 
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from typing import Any

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
                for item in key:
                    self[item]
            case tuple():
                return [self[item] for item in key]
            case InstrumentedAttribute():
                self.select.append(key)
            case BinaryExpression() | BooleanClauseList():
                self.ops.append(("where", key))
            case str():
                return self.__getitem_field(key)
            case slice():
                self.limit = key.stop - key.start
                self.offset = key.start
        return self

    def __build__(self) -> Query:
        query: Query = (
            self.session().query(*(self.select or [self.model])).select_from(self.model)
        )
        for op in self.ops:
            query = getattr(query, op[0])(op[1])
        return query

    def __call__(self, key:str = None):
        if key:
            return self.session().query(self.model).get(key)
        return self.__build__().all()
    
    def __len__(self) -> int:
        return self.__build__().count()

    def __repr__(self) -> str:
        try:
            from sql_formatter.core import format_sql
            return format_sql(str(self.__build__()))
        except:
            return str(self.__build__())

    def __getitem_field(self, key):
        if isinstance(field := getattr(self.model, key, None), InstrumentedAttribute):
            return field
    
    def to_pandas(self):
        try:
            import pandas as pd
        except:
            raise Exception("Pandas is not installed.")
        return pd.read_sql(str(self.__build__()), self.session().connection())