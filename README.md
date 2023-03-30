# iiify
A simple Python Flask-based implementation of the IIIF Image API 1.0 standard

## Notes
* This started as a toy project to learn the IIIF API, so it is not necessarily ready for production, but may be some day.
* It was also an opportunity to learn Flask, a micro-framework. I consciously chose to avoid adding too many abstractions, and attempted to stick to procedural code as much as possible.
* It has a simple on-disk cache scheme, but no cache management.
  * If you want to delete the cache, purge the contents of the cache directory.
  * Cache does not currently check timestamps.
  * Cache can't be disabled yet.
* It was a lot of fun, and does work, but is missing a lot of optimizations.
* There are several sample files in the media directory - all but one are courtesy of the Getty's Open Content Program.

## Installation & Setup
```
git clone https://github.com/ArchiveLabs/iiif.archivelab.org.git
cd iiif.archivelab.org
pip install .
python app.py
```
Navigate to http://127.0.0.1:8080/iiif

You can also run the app using Docker, either with the Flask development server:
```
docker build -t iiify .
docker run -d --rm --name iiify -p 8080:8080 iiify
```
or with an image using nginx and uwsgi:
```
docker build -t iiify-uwsgi -f Dockerfile-uwsgi .
docker run -d --rm --name iiify -p 8080:8080 iiify-uwsgi
```

Navigate to http://127.0.0.1:8080/iiif

## Test it!

Unit tests are in the `tests` folder and can be run with:
```
python -m unittest discover -s tests
```

Retrieve large.jpg as 800px wide JPEG
* http://127.0.0.1:8080/iiif/large.jpg/full/800,/0/default.jpg 

Crop into large.jpg and return 800px wide JPEG
* http://127.0.0.1:8080/iiif/large.jpg/full/800,/0/default.jpg 

Mirror large.jpg horizontally and return 800px wide JPEG
* http://127.0.0.1:8080/iiif/large.jpg/full/800,/!0/default.jpg 

For more information, read the specification at http://iiif.io/technical-details.html
