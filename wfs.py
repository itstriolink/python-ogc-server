import geojson
from pydantic import BaseModel

DEFAULT_LIMIT = 10
MAX_LIMIT = 10000


class WFSLink(BaseModel):
    href: str
    rel: str
    type: str
    title: str


class WFSFeatureCollection(BaseModel):
    type: str
    links: list[WFSLink]
    bounding_Box: float
    Features: list[geojson.Feature]


def format_items_url(prefix, collection, start_id, start, limit, box):
    return None
