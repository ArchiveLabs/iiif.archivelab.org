#!/usr/bin/env python

import os
import requests
from iiif2 import iiif, web
from configs import options, cors, approot, cache_root, media_root, apiurl

CONTEXT = 'http://iiif.io/api/image/2/context.json'
ARCHIVE = 'http://archive.org'
bookdata = 'http://%s/BookReader/BookReaderJSON.php'
bookreader = "http://%s/BookReader/BookReaderImages.php"
valid_filetypes = ['jpg', 'jpeg', 'png', 'gif', 'tif', 'jp2', 'pdf']


def getids(page=1, limit=50):
    r = requests.get('%s/iiif' % apiurl, params={
        'page': page,
        'limit': limit
    }, allow_redirects=True, timeout=None)
    return r.json()
    

def collection(domain, identifiers, label='Custom Archive.org IIIF Collection'):
    cs = {
        '@context': CONTEXT,
        '@id': "%scollection.json" % domain,
        '@type': 'sc:Collection',
        'label': label,
        'collections': []
    }
    for i in identifiers:
        cs['collections'].append({
            '@id': '%s%s/manifest.json' % (domain, i),
            '@type': 'sc:Manifest',
            'label': ''
        })
    return cs

def manifest_page(identifier, label='', page='', width='', height=''):
    return {
        '@id': '%s/canvas' % identifier,
        '@type': 'sc:Canvas',
        'label': label,
        'width': width,
        'height': height,
        'images': [{
            '@type': 'oa:Annotation',
            '@context': CONTEXT,
            '@id': '%s/annotation' % identifier,
            'motivation': "sc:painting",
            'resource': {
                '@id': '%s/full/full/0/default.jpg' % identifier,
                '@type': 'dctypes:Image',
                'width': width,
                'height': height,
                'format': 'image/jpeg',
                'service': {
                    '@context': CONTEXT,
                    '@id': identifier,
                    'profile': 'http://iiif.io/api/image/2/profiles/level2.json',
                }
            }
        }]
    }

def create_manifest(identifier, domain=None):
    manifest = {
        '@context': CONTEXT,
        '@id': '%s%s/manifest.json' % (domain, identifier),
        '@type': 'sc:Manifest',
        'logo': 'http://tinyurl.com/ou7efql',
            'sequences': [
                {
                    '@id': '%s%s/canvas/default' % (domain, identifier),
                    '@type': 'sc:Sequence',
                    '@context': CONTEXT,
                    'label': 'default',
                    'canvases': []
                }
            ],
        'viewingHint': 'paged',
    }
    path = os.path.join(media_root, identifier)
    metadata = requests.get('%s/metadata/%s' % (ARCHIVE, identifier)).json()
    mediatype = metadata['metadata']['mediatype']
    manifest['label'] = metadata['metadata']['title']

    if mediatype.lower() == 'image':
        path, mediatype = ia_resolver(identifier)
        info = web.info(domain, path)
        manifest['sequences'][0]['canvases'].append(
            manifest_page(
                identifier="%s%s" % (domain, identifier),
                label=metadata['metadata']['title'],
                width=info['width'],
                height=info['height']
            )
        )

    elif mediatype.lower() == 'texts':
        subPrefix = metadata['dir']
        server = metadata.get('server', ARCHIVE)

        r = requests.get(bookdata % server, params={
            'server': server,
            'itemPath': subPrefix,
            'itemId': identifier
        })
        data = r.json()

        manifest.update({
            'label': data['title'],
            'thumbnail': {
                '@id': data['previewImage']
            },
        })

        for page in range(1, len(data.get('leafNums', []))):
            manifest['sequences'][0]['canvases'].append(
                manifest_page(
                    identifier = "%s%s$%s" % (domain, identifier, page),
                    label=data['pageNums'][page],
                    width=data['pageWidths'][page],
                    height=data['pageHeights'][page]
                )
            )
    return manifest

def valid_filetype(filename):
    f = filename.lower()
    return any(f.endswith('.%s' % ext) for ext in valid_filetypes)


def ia_resolver(identifier):
    """Resolves a iiif identifier to the resource's path on disk.

    Resolver returns the path of resource on the iiif server (as
    opposed to a remote storage host, like Internet Archive) and first
    fetches it, if it doesn't exist on disk..
    """
    path = os.path.join(media_root, identifier)
    leaf = None
    if "$" in identifier:
        identifier, leaf = identifier.split("$")

    metadata = requests.get('%s/metadata/%s' % (ARCHIVE, identifier)).json()
    if 'dir' not in metadata:
        raise ValueError("No such valid Archive.org item identifier: %s" \
                        % identifier)
    mediatype = metadata['metadata']['mediatype']
    files = metadata['files']
    collections = metadata['metadata']['collection']
    collections = [collections] if isinstance(collections, str) else collections

    # If item in restricted collection, raise permission error
    for i in collections:
        metadata_url = '%s/metadata/%s' % (ARCHIVE, i)
        c = requests.get(metadata_url).json().get('metadata', {})
        if c.get('access-restricted', False):
            raise ValueError("This resource has restricted access")

    if not os.path.exists(path):
        r = None
        if mediatype.lower() == 'image':
            f = next(f for f in files if valid_filetype(f['name']) \
                         and f['source'].lower() == 'original')
            url = '%s/download/%s/%s' % (ARCHIVE, identifier, f['name'])

            r = requests.get(url, stream=True, allow_redirects=True)

        elif mediatype.lower() == 'texts' and leaf:
            r = requests.get('%s/download/%s/page/leaf%s' % (ARCHIVE, identifier, leaf))
        if r:
            with open(path, 'wb') as rc:
                rc.writelines(r.iter_content(chunk_size=1024))

    return path, mediatype
