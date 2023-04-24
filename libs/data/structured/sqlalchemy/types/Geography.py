from marshmallow.fields import Nested
from marshmallow_geojson import GeometryCollectionSchema, GeoJSONSchema
from marshmallow_sqlalchemy.convert import ModelConverter
from shapely.geometry import GeometryCollection
from sqlalchemy.dialects.mssql.base import ischema_names as mssql_ischema_names
import geoalchemy2.types
import geojson
import shapely.wkb

import logging


# class Geometry(geoalchemy2.types.Geometry):
#     def result_processor(self, dialect, coltype):
#         def process(value):
#             wkb = shapely.wkb.loads(value) if value else value
#             # match cls := getattr(geojson,shape.type, None):
#             #     case geojson.GeometryCollection:
#             #         return cls(geometries=[geojson.Feature(geometry=o) for o in shape.geoms])
#             #     case _:
#             #         return geojson.Feature(geometry=shape)
#             return geojson.GeometryCollection(
#                 geometries=wkb.geoms if type(wkb) == GeometryCollection else [wkb]
#             )

#         return process

#     def bind_processor(self, dialect):
#         def process(value):
#             return shapely.wkb.loads(value) if value else value

#         return process


# class Geography(Geometry):
#     pass


# mssql_ischema_names["geometry"] = Geometry
# mssql_ischema_names["geography"] = Geography


# class GeometryField(Nested):
#     def __init__(self, **kwargs):
#         super().__init__(GeometryCollectionSchema, **kwargs)


# ModelConverter.SQLA_TYPE_MAPPING[Geometry] = GeometryField
# ModelConverter.SQLA_TYPE_MAPPING[Geography] = GeometryField


from libs.utils.geometry import wkb2geojson, geojson2wkb


class GeometryJSON(geoalchemy2.types.Geometry):
    def result_processor(self, dialect, coltype):
        def process(value):
            return wkb2geojson(value) if value else value

        return process

    def bind_processor(self, dialect):
        def process(value):
            return geojson2wkb(value) if value else value

        return process


class GeographyJSON(GeometryJSON):
    pass


mssql_ischema_names["geometry"] = GeometryJSON
mssql_ischema_names["geography"] = GeographyJSON


class GeoJSONField(Nested):
    def __init__(self, **kwargs):
        super().__init__(GeoJSONSchema, **kwargs)


ModelConverter.SQLA_TYPE_MAPPING[GeometryJSON] = GeoJSONField
ModelConverter.SQLA_TYPE_MAPPING[GeographyJSON] = GeoJSONField
