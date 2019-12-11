#!/usr/bin/env python

import os
import requests
from iiif2 import iiif, web
from configs import options, cors, approot, cache_root, media_root, apiurl

IMG_CTX = 'http://iiif.io/api/image/2/context.json'
PRZ_CTX = 'http://iiif.io/api/presentation/2/context.json'
ARCHIVE = 'http://archive.org'
METADATA_FIELDS = ("title", "volume", "publisher", "subject", "date", "contributor", "creator")
bookdata = 'http://%s/BookReader/BookReaderJSON.php'
bookreader = "http://%s/BookReader/BookReaderImages.php"
valid_filetypes = ['jpg', 'jpeg', 'png', 'gif', 'tif', 'jp2', 'pdf']

def purify_domain(domain):
    return domain if domain.endswith('/iiif/') else domain + 'iiif/'

def getids(q, limit=1000, cursor=''):
    r = requests.get('%s/iiif' % apiurl, params={
        'q': q,
        'limit': limit,
        'cursor': cursor
    }, allow_redirects=True, timeout=None)
    return r.json()


def collection(domain, identifiers, label='Custom Archive.org IIIF Collection'):
    cs = {
        '@context': PRZ_CTX,
        '@id': "%scollection.json" % domain,
        '@type': 'sc:Collection',
        'label': label,
        'collections': []
    }
    for i in identifiers:
        cs['collections'].append({
            '@id': '%s%s/manifest.json' % (domain, i),
            '@type': 'sc:Manifest',
            'label': label,
            'description': label
        })
    return cs

def manifest_page(identifier, label='', page='', width='', height='', metadata=None):
    metadata = metadata or {}
    return {
        '@id': '%s/canvas' % identifier,
        '@type': 'sc:Canvas',
        '@context': PRZ_CTX,
        'description': metadata.get('description', ''),
        'label': label or 'p. ' + str(page),
        'width': width,
        'height': height,
        'images': [{
            '@type': 'oa:Annotation',
            '@context': IMG_CTX,
            '@id': '%s/annotation' % identifier,
            'on': '%s/annotation' % identifier,
            'motivation': "sc:painting",
            'resource': {
                '@id': '%s/full/full/0/default.jpg' % identifier,
                '@type': 'dctypes:Image',
                'width': width,
                'height': height,
                'format': 'image/jpeg',
                'service': {
                    '@context': IMG_CTX,
                    '@id': identifier,
                    'profile': 'https://iiif.io/api/image/2/profiles/level2.json',
                }
            }
        }]
    }


def create_manifest(identifier, domain=None, page=None):
    path = os.path.join(media_root, identifier)
    resp = requests.get('%s/metadata/%s' % (ARCHIVE, identifier)).json()
    metadata = resp.get("metadata", {})

    manifest = {
        '@context': PRZ_CTX,
        '@id': '%s%s/manifest.json' % (domain, identifier),
        '@type': 'sc:Manifest',
        'description': metadata.get('description', ''),
        'logo': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcReMN4l9cgu_qb1OwflFeyfHcjp8aUfVNSJ9ynk2IfuHwW1I4mDSw',
            'sequences': [
                {
                    '@id': '%s%s/canvas/default' % (domain, identifier),
                    '@type': 'sc:Sequence',
                    '@context': IMG_CTX,
                    'label': 'default',
                    'canvases': []
                }
            ],
        'viewingHint': 'paged',
        'attribution': "The Internet Archive",
        'seeAlso': '%s/metadata/%s' % (ARCHIVE, identifier)
    }

    mediatype = metadata.get("mediatype")

    if 'title' in metadata:
        manifest['label'] = metadata['title']
    if 'identifier-access' in metadata:
        manifest['related'] = metadata['identifier-access']
    if 'description' in metadata:
        manifest['description'] = coerce_list(metadata['description'])

    manifest['metadata'] = [{"label": field, "value": coerce_list(metadata[field])}
                            for field in METADATA_FIELDS if metadata.get(field)]

    if page and mediatype is None:
        mediatype = 'image'

    if "$" not in identifier:
        filepath = None
    else:
        identifier, filepath = identifier.split("$", 1)
        filepath = filepath.replace("$", os.sep)

    if mediatype.lower() == 'image' or (
        filepath and mediatype.lower() != 'texts'
    ):
        path, mediatype = ia_resolver(identifier)
        info = web.info(domain, path)
        manifest['sequences'][0]['canvases'].append(
            manifest_page(
                identifier="%s%s" % (domain, identifier),
                label=metadata['title'],
                width=info['width'],
                height=info['height'],
                metadata=metadata
            )
        )

    elif mediatype.lower() == 'texts':
        subPrefix = resp['dir']
        server = resp.get('server', ARCHIVE)

        # XXX Use https://api.archivelab.org/books/:id/metadata API

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

        if page:
            manifest['sequences'][0]['canvases'].append(
                manifest_page(
                    identifier = "%s%s$%s" % (domain, identifier, page),
                    label=data['pageNums'][page],
                    width=data['pageWidths'][page],
                    height=data['pageHeights'][page]
                )
            )
            return manifest

        for page in range(0, len(data.get('leafNums', []))):
            manifest['sequences'][0]['canvases'].append(
                manifest_page(
                    identifier = "%s%s$%s" % (domain, identifier, page),
                    label=data['pageNums'][page],
                    width=data['pageWidths'][page],
                    height=data['pageHeights'][page]
                )
            )
    return manifest


def coerce_list(value):
    if isinstance(value, list):
        return ". ".join(value)
    return value


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
    if "$" not in identifier:
        filepath = None
    else:
        identifier, filepath = identifier.split("$", 1)
        filepath = filepath.replace("$", os.sep)
        if os.sep not in filepath:
            leaf = filepath

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
            # check for preview, e.g. etable of contents (which can be public?)
            # ...
            raise ValueError("This resource has restricted access")

    if not os.path.exists(path):
        r = None

        if mediatype.lower() == 'image' or (
            filepath and mediatype.lower() != 'texts'
        ):
            if filepath:
                itempath = os.path.join(identifier, filepath)
            else:
                f = next(f for f in files if valid_filetype(f['name']) \
                         and f['source'].lower() == 'original')
                itempath = os.path.join(identifier, f['name'])
            url = '%s/download/%s' % (ARCHIVE, itempath)
            print(url)
            r = requests.get(url, stream=True, allow_redirects=True)

        elif mediatype.lower() == 'texts' and leaf:
            url = '%s/download/%s/page/leaf%s' % (ARCHIVE, identifier, leaf)
            r = requests.get(url)
        if r:
            with open(path, 'wb') as rc:
                rc.writelines(r.iter_content(chunk_size=1024))

    return path, mediatype
