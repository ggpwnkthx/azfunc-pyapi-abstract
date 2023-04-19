from functools import partial
from pyproj import Proj, transform as pyproj_transform
from shapely.geometry import (
    shape,
    GeometryCollection,
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    polygon,
    multipolygon,
)
from shapely.ops import transform as shapely_transform
from typing import Union
import numpy as np
import geojson
import shapely.wkt

GeoJsonType: type = Union[geojson.Feature, geojson.FeatureCollection]
WktType: type = Union[
    GeometryCollection,
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
]


def wkt2geojson(wkt: str) -> GeoJsonType:
    wkt = shapely.wkt.loads(wkt)
    wkt = validate_wkt(wkt)
    if type(wkt) == GeometryCollection:
        features = [geojson.Feature(geometry=o, properties={}) for o in wkt.geoms]
        feature_collection = geojson.FeatureCollection(features)
        return feature_collection
    else:
        feature = geojson.Feature(geometry=wkt, properties={})
        return feature


def geojson2shape(
    data: Union[GeoJsonType, dict]
) -> Union[GeometryCollection, Polygon, MultiPolygon,]:
    data = validate_geojson(data)
    if data.get("type") == "Polygon":
        return polygon.orient(shape(data), sign=1.0)
    elif data.get("type") == "MultiPolygon":
        return MultiPolygon(
            [polygon.orient(poly, sign=1.0) for poly in shape(data).geoms]
        )
    elif data.get("type") == "Feature":
        return geojson2shape(data.get("geometry"))
    elif data.get("type") == "FeatureCollection":
        g = [geojson2shape(f.get("geometry")) for f in data.get("features")]
        return GeometryCollection(g)
    else:
        raise Exception


def geojson2wkt(data: Union[GeoJsonType, dict]) -> WktType:
    return geojson2shape(validate_geojson(data)).wkt


def validate_geojson(data: Union[GeoJsonType, dict]) -> GeoJsonType:
    data = geojson.loads(geojson.dumps(data))
    if not data.is_valid:
        return None

    return data


def validate_wkt(data: WktType) -> WktType:
    if not data.is_valid:
        return None
    return data


def latlon_buffer(lat: float, lon: float, radius: int, cap_style=int):
    """
    Creates a buffer circle around a latlong point with a given radius in meters.

    Params:
    cap_style: round = 1, flat = 2, square = 3

    Modified from latlon_circle
    """

    local_azimuthal_projection = (
        "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lat, lon)
    )
    wgs84_to_aeqd = partial(
        pyproj_transform,
        Proj("+proj=longlat +datum=WGS84 +no_defs"),
        Proj(local_azimuthal_projection),
    )
    aeqd_to_wgs84 = partial(
        pyproj_transform,
        Proj(local_azimuthal_projection),
        Proj("+proj=longlat +datum=WGS84 +no_defs"),
    )

    point_transformed = shapely_transform(wgs84_to_aeqd, Point(float(lon), float(lat)))
    buffer = point_transformed.buffer(radius, cap_style=cap_style)
    # Get the polygon with lat lon coordinates
    buffered_poly = shapely_transform(aeqd_to_wgs84, buffer)
    return buffered_poly


def points_in_poly_numpy(x: np.array, y: np.array, poly: np.array) -> np.array:
    """
    Finds points that are within given polygon coordinates.
    Uses numpy to vectorize and check all points quickly

    Args:
        x       : x-coordinates of the points to check
        y       : y-coordinates of the points to check
        poly    : coordinates of the polygon

    Returns:
        inside: boolean array the length of the points. True if the point is inside the polygon, False otherwise
    """

    n = len(poly)

    # initialize an array for returns
    inside = np.zeros(len(x), np.bool_)

    # and set up some 'blank' variables we'll use later
    p2x = 0.0
    p2y = 0.0
    xints = 0.0

    # start out with the first point on the polygon
    p1x, p1y = poly[0]

    # loop through the polygon coordinates
    for i in range(1, n + 1):
        # modulo the polygon coordinates since we need it to close back on the first one
        p2x, p2y = poly[i % n]

        # check if the point is within the y-bounds and not greater than the max x of the poly coordinates
        idx = np.nonzero(
            (y > min(p1y, p2y)) & (y <= max(p1y, p2y)) & (x <= max(p1x, p2x))
        )[0]

        # if the point is in that region
        if len(idx):
            # if the two polygon coords aren't in a horizontal line
            if p1y != p2y:
                # find the x where the point projects horizontally onto the line between polygon coordinates
                xints = (y[idx] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x

            # if the two polygon coords are in a vertical line
            if p1x == p2x:
                # the point then falls on the line between the two points and is counted (edge inclusion)
                inside[idx] = ~inside[idx]
            else:
                # check if the x point is to left of the intercept and count those that are
                idxx = idx[x[idx] <= xints]
                inside[idxx] = ~inside[idxx]

        # set p1 to the next polygon coordinate
        p1x, p1y = p2x, p2y

    return inside
