# Python OGC Feature and Tile Server

This is a mini OGC API server compliant with the [OGC API - Features](https://docs.opengeospatial.org/is/17-069r3/17-069r3.html)
 
It serves GeoJSON objects and PNG raster tiles.

**Available API methods:**

*  ***OGC API methods***:
1. */collections*
2. */collections/{collection}*
3. */collections/{collection}/items?{bbox}*
4. */collections{collection}/items/{feature_id}*

* ***Other methods:***
1. */tiles/{collection}/{zoom}/{x}/{y}.png*
2. */tiles/{collection}/{zoom}/{x}/{y}/{a}/{b}.geojson*
