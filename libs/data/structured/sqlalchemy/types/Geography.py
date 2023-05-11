try:
    from marshmallow.fields import Nested
    from marshmallow_geojson import GeoJSONSchema
    from marshmallow_sqlalchemy.convert import ModelConverter
    from sqlalchemy.dialects.mssql.base import ischema_names as mssql_ischema_names
    import geoalchemy2.types


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
except:
    pass