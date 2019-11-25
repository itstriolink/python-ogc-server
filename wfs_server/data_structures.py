class CollectionMetadata:
    name: str
    path: str
    last_modified: str

    def __init__(self, name, path, last_modified):
        self.name = name
        self.path = path
        self.last_modified = last_modified


class Collection:
    metadata: CollectionMetadata
    offset: [] = []
    bbox: [] = []
    web_mercator: [] = []
    id: [] = []
    by_id: {} = {}
    feature: [] = []


class WFSLink:
    href: str
    rel: str
    type: str
    title: str

    def to_json(self):
        return dict(href=self.href, rel=self.rel, type=self.type, title=self.title)
