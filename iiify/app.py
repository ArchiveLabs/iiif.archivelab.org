#!/usr/bin/env python

import os
import requests
from flask import Flask, send_file, jsonify, abort, request, render_template
from flask.ext.cors import CORS
from iiif2 import iiif, web
from resolver import ia_resolver, create_manifest
from configs import options, cors, approot, cache_root, media_root, \
    cache_expr, version, apiurl


app = Flask(__name__)
cors = CORS(app) if cors else None


@app.route('/')
def index():
    """Lists all available book and image items on Archive.org"""
    page = request.args.get("page", 1)
    limit = min(int(request.args.get("limit", 50)), 100)
    r = requests.get("%s/items" % apiurl, params={
        "page": page,
        "limit": limit,
        "filters": "(mediatype:(texts) OR mediatype:(image))"
    })
    return jsonify(r.json())


@app.route('/cache')
def cache():
    """Lists all recently cached images"""
    return jsonify({'identifiers': [f for f in os.listdir(media_root)]})


@app.route('/demo')
def demo():
    domain = "https://purl.stanford.edu/kq131cs7229/iiif"
    return render_template('reader.html', domain=domain)

@app.route('/documentation')
def documentation():
    return render_template('docs/index.html', version=version)


@app.route('/<identifier>')
def view(identifier):
    domain = request.args.get('domain', request.url_root)
    uri = '%s%s' % (domain, identifier)
    path, mediatype = ia_resolver(identifier)
    if mediatype == 'image' or '$' in identifier:
        return render_template('viewer.html', domain=domain,
                               info=web.info(uri, path))
    return render_template('reader.html', domain=request.base_url)


@app.route('/<identifier>/manifest.json')
def manifest(identifier):
    domain = request.args.get('domain', request.url_root)
    return jsonify(create_manifest(identifier, domain=domain))


@app.route('/<identifier>/info.json')
def info(identifier):
    try:
        domain = '%s%s' % (request.url_root, identifier)
        path, mediatype = ia_resolver(identifier)
        info = web.info(domain, path)
        return jsonify(info)
    except:
        abort(400)


@app.route('/<identifier>/<region>/<size>/<rotation>/<quality>.<fmt>')
def image_processor(identifier, **kwargs):
    cache_path = os.path.join(cache_root, web.urihash(request.path))

    if os.path.exists(cache_path):
        mime = iiif.type_map[kwargs.get('fmt')]['mime']
        return send_file(cache_path, mimetype=mime)

    try:
        params = web.Parse.params(identifier, **kwargs)
        path, _ = ia_resolver(identifier)
        tile = iiif.IIIF.render(path, **params)
        tile.save(cache_path, tile.mime)
        return send_file(tile, mimetype=tile.mime)
    except Exception as e:
        abort(400)


@app.after_request
def add_header(response):
    response.cache_control.max_age = cache_expr  # minutes
    return response


if __name__ == '__main__':
    app.run(**options)
