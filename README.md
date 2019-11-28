# Python Tile Server

This is a MiniWFS server compliant with WFS3, written in Python that serves GeoJSON objects and PNG raster tiles.

**Available API methods:**
1. */collections*
2. */collections/{collection_name}*
3. */collections/{collection_name}/items?{bbox}{limit}*
4. */collections{collection_name}/items/{feature_id}*
5. */tiles/{collection_name}/{zoom}/{x}/{y}.png*
6. */tiles/{collection_name}/{zoom}/{x}/{y}/{a}/{b}.geojson*
