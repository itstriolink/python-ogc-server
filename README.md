# Python Tile Server

This is a MiniWFS server compliant with WFS3, written in Python that serves GeoJSON objects and PNG raster tiles.

**Available API methods:**

*  ***WFS3 methods***:
1. */collections*
2. */collections/{collection}*
3. */collections/{collection}/items?{bbox}{limit}*
4. */collections{collection}/items/{feature_id}*

* ***Other methods:***
1. */tiles/{collection}/{zoom}/{x}/{y}.png*
2. */tiles/{collection}/{zoom}/{x}/{y}/{a}/{b}.geojson*
