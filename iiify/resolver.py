
#!/usr/bin/env python

import os
import requests
from configs import options, cors, approot, cache_root, media_root

archive = 'https://archive.org'
bookdata = 'http://%s/BookReader/BookReaderJSON.php'
bookreader = "http://%s/BookReader/BookReaderImages.php"
valid_filetypes = ['jpg', 'png', 'gif', 'tif']

def create_manifest(identifier, domain=None):
    manifest = {}
    path = os.path.join(media_root, identifier)
    metadata = requests.get('%s/metadata/%s' % (archive, identifier)).json()
    mediatype = metadata['metadata']['mediatype']

    if mediatype.lower() == 'texts':
        subPrefix = metadata['dir']
        server = metadata.get('server', 'https://archive.org')

        r = requests.get(bookdata % server, params={
            'server': server,
            'itemPath': subPrefix,
            'itemId': identifier
        })
        data = r.json()
        context = 'http://iiif.io/api/image/2/context.json'
        manifest = {
            '@context': context,
            '@id': '%s%s/manifest.json' % (domain, identifier),
            '@type': 'sc:Manifest',
            'logo': 'http://tinyurl.com/ou7efql',
            'label': data['title'],
            'viewingHint': 'paged',
            'sequences': [
                {
                    '@id': '%s%s/canvas/default' % (domain, identifier),
                    '@type': 'sc:Sequence',
                    '@context': context,
                    'label': 'default',
                    'canvases': []
                }
            ],
            'thumbnail': {
                '@id': data['previewImage']
            },
        }
        for page in range(1, len(data.get('leafNums', []))):
            manifest['sequences'][0]['canvases'].append({
                '@id': '%s%s$%s/canvas' % (domain, identifier, page),
                '@type': 'sc:Sequence',
                'label': data['pageNums'][page],
                'width': data['pageWidths'][page],
                'height': data['pageHeights'][page],
                'images': [{
                    'type': 'oa:Annotation',
                    '@context': context,
                    '@id': '%s%s$%s/annotation' % (domain, identifier, page),
                    'motivation': "sc:painting",
                    'resource': {
                        '@id': '%s%s$%s/full/full/0/default.jpg' % \
                        (domain, identifier, page),
                        '@type': 'dctypes:Image',
                        'width': data['pageWidths'][page],
                        'height': data['pageHeights'][page],
                        'format': 'image/jpeg',
                        'service': {
                            '@context': context,
                            '@id': '%s%s$%s' % \
                            (domain, identifier, page),
                            'profile': 'http://iiif.io/api/image/2/profiles/level2.json',
                        }
                    }                    
                }]
            })
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

    metadata = requests.get('%s/metadata/%s' % (archive, identifier)).json()

    if 'dir' not in metadata:
        raise Exception("No such valid Archive.org item identifier: %s" \
                        % identifier)
    mediatype = metadata['metadata']['mediatype']
    files = metadata['files']

    if not os.path.exists(path):
        r = None
        if mediatype.lower() == 'image':
            f = next(f for f in files if valid_filetype(f['name']) \
                         and f['source'].lower() == 'original')
            url = '%s/download/%s/%s' % (archive, identifier, f['name'])

            r = requests.get(url, stream=True, allow_redirects=True)

        elif mediatype.lower() == 'texts' and leaf:
            r = requests.get('%s/download/%s/page/leaf%s' % (archive, identifier, leaf))
        if r:
            with open(path, 'wb') as rc:
                rc.writelines(r.iter_content(chunk_size=1024))

    return path, mediatype
