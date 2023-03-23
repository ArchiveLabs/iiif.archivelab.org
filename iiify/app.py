#!/usr/bin/env python

import os
import time
from flask import Flask, send_file, jsonify, abort, request, render_template, redirect
from flask_cors import CORS
from iiif2 import iiif, web
from .resolver import ia_resolver, create_manifest, getids, collection, \
    purify_domain
from .url2iiif import url2ia
from .configs import options, cors, approot, cache_root, media_root, \
    cache_expr, version


app = Flask(__name__)
cors = CORS(app) if cors else None

def sprite_concat(imgs):
    from PIL import Image
    images = list(map(Image.open, imgs))
    widths, heights = zip(*[i.size for i in images])

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    return new_im

@app.route('/iiif/')
def index():
    """Lists all available book and image items on Archive.org"""
    cursor = request.args.get('cursor', '')
    q = request.args.get('q', '')
    return jsonify(getids(q, cursor=cursor))

@app.route('/iiif/url2iiif')
def url2iiif():
    url = request.args.get('url', '')
    if not url:
        abort(400)
    try:
        domain = purify_domain(request.args.get('domain', request.url_root))
        filehash = url2ia(url)
        time.sleep(20)
        return redirect('%surl2iiif$%s' % (domain, filehash))
    except Exception as e:
        print(e)
        abort(400)

@app.route('/iiif/collection.json')
def catalog():
    cursor = request.args.get('cursor', '')
    q = request.args.get('q', '')
    domain = purify_domain(request.args.get('domain', request.url_root))
    return ldjsonify(collection(domain, getids(q, limit, cursor)['ids']))

@app.route('/iiif/cache')
def cache():
    """Lists all recently cached images"""
    return jsonify({'identifiers': [f for f in os.listdir(media_root)]})


@app.route('/iiif/demo')
def demo():
    domain = "http://dms-data.stanford.edu/data/manifests/Stanford/ege1"
    return render_template('reader.html', domain=domain)


@app.route('/iiif/documentation')
def documentation():
    return render_template('docs/index.html', version=version)

@app.route('/iiif/<identifier>')
def view(identifier):
    domain = purify_domain(request.args.get('domain', request.url_root))
    uri = '%s%s' % (domain, identifier)
    page = request.args.get('page', None)
    citation = request.args.get('citation', None)

    try:
        path, mediatype = ia_resolver(identifier)
    except ValueError:
        abort(404)
    if mediatype == 'image' or '$' in identifier:
        return render_template('viewer.html', domain=domain,
                               info=web.info(uri, path))
    return render_template('reader.html', domain=request.base_url, page=page, citation=citation)


@app.route('/iiif/<identifier>/manifest.json')
def manifest(identifier):
    domain = purify_domain(request.args.get('domain', request.url_root))
    page = None
    if '$' in identifier:
        identifier, page = identifier.split('$')
        page = int(page)
    try:
        return ldjsonify(create_manifest(identifier, domain=domain, page=page))
    except:
        abort(404)


@app.route('/iiif/<identifier>/info.json')
def info(identifier):
    try:
        path, mediatype = ia_resolver(identifier)
    except ValueError:
        abort(404)
    try:
        domain = '%s%s' % (purify_domain(request.url_root), identifier)
        info = web.info(domain, path)
        return ldjsonify(info)
    except:
        abort(400)  # , "Invalid item, may actually be collection")


@app.route('/iiif/<identifier>/<region>/<size>/<rotation>/<quality>.<fmt>')
def image_processor(identifier, **kwargs):
    cache_path = os.path.join(cache_root, web.urihash(request.path))

    if os.path.exists(cache_path):
        mime = iiif.type_map[kwargs.get('fmt')]['mime']
        return send_file(cache_path, mimetype=mime)

    identifiers = identifier.split(',') if ',' in identifier else [identifier]
    sprite_tiles = []
    for _id in identifiers:
        try:
            path, _ = ia_resolver(_id)
        except:
            abort(404)
        try:
            params = web.Parse.params(_id, **kwargs)
            tile = iiif.IIIF.render(path, **params)
            tile_cache_path = os.path.join(cache_root, web.urihash(request.path.replace(identifier, _id)))
            tile.seek(0)
            tile.save(tile_cache_path, tile.mime)
            sprite_tiles.append(tile)
        except Exception as e:
            abort(404)

    if len(sprite_tiles) == 1:
        tile = sprite_tiles[0]
    else:
        tile = iiif.IIIF.format(sprite_concat(sprite_tiles), fmt=kwargs.get('fmt'))
        tile.seek(0)
        print(cache_path)
        tile.save(cache_path, tile.mime)

    try:
        tile.seek(0)
        return send_file(tile, mimetype=tile.mime)
    except Exception as e:
        abort(400)


@app.after_request
def add_header(response):
    response.cache_control.max_age = cache_expr  # minutes
    return response


def ldjsonify(data):
    j = jsonify(data)
    j.headers.set('Access-Control-Allow-Origin', '*')
    j.mimetype = "application/ld+json"
    return j

if __name__ == '__main__':
    app.run(**options)
