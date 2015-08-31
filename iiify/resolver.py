#!/usr/bin/env python

import os
import requests
from configs import options, cors, approot, cache_root, media_root

archive = 'https://archive.org'
bookdata = '%s/BookReader/BookReaderJSON.php' % (archive)
bookreader = "%s/BookReader/BookReaderImages.php" % (archive)


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
    server = metadata.get('server', 'https://archive.org')
    subPrefix = metadata['dir']
    mediatype = metadata['metadata']['mediatype']
    files = metadata['files']

    if not os.path.exists(path):
        if mediatype.lower() == 'image':
            f = next(f for f in files if f['name'].lower().endswith('.jpg') \
                         and f['source'].lower() == 'original')

            r = requests.get('%s/download/%s/%s' % (archive, identifier, f['name']),
                             stream=True, allow_redirects=True)

        elif mediatype.lower() == 'texts':
            if not leaf:
                raise
            r = requests.get('%s/download/%s/page/%s' % (archive, identifier, leaf))

        with open(path, 'wb') as rc:
            rc.writelines(r.iter_content(chunk_size=1024))

    return path
