DEFAULT_LIMIT = 10
MAX_LIMIT = 10000


class WFSLink:
    href: str
    rel: str
    type: str
    title: str


class WFSFeatureCollection:
    type: str
    links: []
    bounding_box: []
    Features: []


def format_items_url(prefix, collection, start_id, start, limit, box):
    return None
