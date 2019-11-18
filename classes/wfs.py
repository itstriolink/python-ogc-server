DEFAULT_LIMIT = 10
MAX_LIMIT = 10000


class WFSLink:
    href: str
    rel: str
    type: str
    title: str

    def to_json(self):
        return dict(href=self.href, rel=self.rel, type=self.type, title=self.title)


class WFSFeatureCollection:
    type: str
    links: []
    bounding_box: []
    Features: []


def format_items_url(prefix, collection, start_id, start, limit, box):
    return None
