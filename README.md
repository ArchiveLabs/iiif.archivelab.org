# iiify
A simple Python Flask-based implementation of the IIIF Image API 2.0 standard

## Notes
* This started as a toy project to learn the IIIF API, so it is not necessarily ready for production, but may be some day.
* It was also an opportunity to learn Flask, a micro-framework. I consciously chose to avoid adding too many abstractions, and attempted to stick to procedural code as much as possible.
* It has a simple on-disk cache scheme, but no cache management.
  * If you want to delete the cache, purge the contents of the cache directory.
  * Cache does not currently check timestamps.
  * Cache can't be disabled yet.
* It was a lot of fun, and does work, but is missing a lot of optimizations.
* There are several sample files in the media directory - all but one are courtesy of the Getty's Open Content Program.

## Simple instructions
```
pip install Flask Pillow
python iiify.py
```

## Less simple instructions
1. Clone this repo
2. Setup a virtualenv (optional)
3. do `pip install Flask Pillow`
4. do `python iiify.py`
5. You now have a simple IIIF server running at http://127.0.0.1:5000

## Test it!

Retrieve large.jpg as 800px wide JPEG
* http://127.0.0.1:5000/large.jpg/full/800,/0/default.jpg 

Crop into large.jpg and return 800px wide JPEG
* http://127.0.0.1:5000/large.jpg/full/800,/0/default.jpg 

Mirror large.jpg horizontally and return 800px wide JPEG
* http://127.0.0.1:5000/large.jpg/full/800,/!0/default.jpg 

For more information, read the specification at http://iiif.io/technical-details.html
