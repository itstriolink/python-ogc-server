# Python OGC Feature and Tile Server

This is a dockerized OGC API server that is minimally compliant with the [OGC API - Features (OAPIF)](https://docs.opengeospatial.org/is/17-069r3/17-069r3.html) standard.

It serves GeoJSON objects and PNG raster tiles.

**Available API endpoints:**

*  ***OAPIF endpoints***:
1. */collections*
2. */collections/{collection}*
3. */collections/{collection}/items*
4. */collections{collection}/items/{feature_id}*

* ***Tile endpoints:***
1. */tiles/{collection}/{zoom}/{x}/{y}.png*
2. */tiles/{collection}/{zoom}/{x}/{y}/{a}/{b}.geojson*


To use it, just point any OGC API client to it.