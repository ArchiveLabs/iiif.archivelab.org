#!/usr/bin/env python

import os
from flask import Flask, send_file, jsonify, abort, request, render_template
from flask.ext.cors import CORS
from iiif2 import iiif, web
from resolver import ia_resolver
from configs import options, cors, approot, cache_root, media_root, cache_expr

app = Flask(__name__)
cors = CORS(app) if cors else None


@app.route('/')
def index():
    return jsonify({'identifiers': [f for f in os.listdir(media_root)]})


@app.route('/<identifier>/info.json')
def image_info(identifier):
    try:
        info = web.info(identifier, ia_resolver(identifier))
        return jsonify(info)
    except:
        abort(400)


@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/<identifier>', defaults={'quality': 'default', 'fmt': 'jpg'})
@app.route('/<identifier>/view/<quality>.<fmt>')
def view(identifier, quality="default", fmt="jpg"):
    domain = request.args.get('domain', request.url_root)
    uri = '%s%s' % (domain, identifier)
    return render_template('viewer.html', domain=domain,
                           info=web.info(uri, ia_resolver(identifier)))


@app.route('/<identifier>/<region>/<size>/<rotation>/<quality>.<fmt>')
def image_processor(identifier, **kwargs):
    cache_path = os.path.join(cache_root, web.urihash(request.path))

    if os.path.exists(cache_path):
        mime = iiif.type_map[kwargs.get('fmt')]['mime']
        return send_file(cache_path, mimetype=mime)

    try:
        params = web.Parse.params(identifier, **kwargs)
        tile = iiif.IIIF.render(ia_resolver(identifier), **params)
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
