from fastapi import HTTPException


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


HTTPResponse = {
    "NOT_FOUND": HTTPException(status_code=404, detail="Collection not found"),
    "BAD_REQUEST": HTTPException(status_code=400, detail="Malformed parameters"),
    "NOT_MODIFIED": HTTPException(status_code=304, detail="Not Modified"),
    "INTERNAL_ERROR": HTTPException(status_code=500, detail="Internal server error occurred"),
}


class APIResponse:
    content: object
    http_response: HTTPException

    def __init__(self, content, http_response):
        self.content = content
        self.http_response = http_response
