#!/usr/bin/env python

import os
import requests
from iiif2 import iiif, web
from .configs import options, cors, approot, cache_root, media_root, apiurl
from iiif_prezi3 import Manifest, config, Annotation, AnnotationPage, Canvas, Manifest, ResourceItem, ServiceItem, Choice, Collection, ManifestRef, CollectionRef
from urllib.parse import urlparse, parse_qs
import json
import math 

IMG_CTX = 'http://iiif.io/api/image/2/context.json'
PRZ_CTX = 'http://iiif.io/api/presentation/2/context.json'
ARCHIVE = 'http://archive.org'
IMG_SRV = 'https://services-ia-iiif-cantaloupe-experiment.dev.archive.org/iiif'
METADATA_FIELDS = ("title", "volume", "publisher", "subject", "date", "contributor", "creator")
bookdata = 'http://%s/BookReader/BookReaderJSON.php'
bookreader = "http://%s/BookReader/BookReaderImages.php"
valid_filetypes = ['jpg', 'jpeg', 'png', 'gif', 'tif', 'jp2', 'pdf', 'tiff']

def purify_domain(domain):
    return domain if domain.endswith('/iiif/') else domain + 'iiif/'

def getids(q, limit=1000, cursor=''):
    r = requests.get('%s/iiif' % apiurl, params={
        'q': q,
        'limit': limit,
        'cursor': cursor
    }, allow_redirects=True, timeout=None)
    return r.json()

def to_mimetype(format):
    formats = {
        "VBR MP3": "audio/mp3",
        "32Kbps MP3": "audio/mp3",
        "56Kbps MP3": "audio/mp3",
        "64Kbps MP3": "audio/mp3",
        "96Kbps MP3": "audio/mp3",
        "128Kbps MP3": "audio/mp3",
        "Flac": "audio/flac",
        "Ogg Vorbis": "audio/ogg",
        "Ogg Video": "video/ogg",
        "WAVE": "audio/wav",
        "MPEG4": "video/mp4",
        "24bit Flac": "audio/flac",
        'Shorten': "audio/shn",
        "MPEG2": "video/mpeg",
        "512Kb MPEG4": "video/mpeg",
        "HiRes MPEG4": "video/mpeg",
        "h.264 MPEG4": "video/mpeg",
        "h.264": "video/mpeg",
        "Matroska": "video/x-matroska",
        "Cinepack": "video/x-msvideo",
        "AIFF": "audio/aiff",
        "Apple Lossless Audio": "audio/x-m4a",
        "MPEG-4 Audio": "audio/mp4" 
    }
    return formats.get(format, "application/octet-stream")

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

def create_collection3(identifier, domain, page=1, rows=1000):
    # Get item metadata
    metadata = requests.get('%s/metadata/%s' % (ARCHIVE, identifier)).json()

    # Used to build up URIs for the manifest
    uri = f"{domain}3/{identifier}/collection.json"

    config.configs['helpers.auto_fields.AutoLang'].auto_lang = "none"
    collection = Collection(id=uri, label=metadata["metadata"]["title"])

    addMetadata(collection, identifier, metadata['metadata'], collection=True)

    asURL = f'https://archive.org/advancedsearch.php?q=collection%3A{identifier}&fl[]=identifier&fl[]=mediatype&fl[]=title&fl[]=description&sort[]=&sort[]=&sort[]=&rows={rows}&page={page}&output=json&save=yes'
    itemsSearch = requests.get(asURL).json()
    total = itemsSearch['response']['numFound']
    # There is a max of 10,000 items that can be retrieved from the advanced search
    if total > 10000:
        total = 10000

    if len(itemsSearch['response']['docs']) == 0:
        return None 

    pages = math.ceil(total / rows)
    for item in itemsSearch['response']['docs']:
        child = None
        if item['mediatype'] == 'collection':
            child = CollectionRef(id=f"{domain}3/{item['identifier']}/collection.json", type="Collection", label=item['title'])
        else: 
            child = ManifestRef(id=f"{domain}3/{item['identifier']}/manifest.json", type="Manifest", label=item['title'])
        
        if "description" in item:
            child.summary = {"none": [item['description']]} 

        collection.add_item(child)
    page += 1
    if page <= pages:
        child = CollectionRef(id=f"{domain}3/{identifier}/{page}/collection.json", type="Collection", label={ "en": [f"Page {page} of {pages}"]})
        collection.add_item(child)

    print ('Returning collection')
    return json.loads(collection.jsonld())
    
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

def singleImage(metadata, identifier, manifest, uri):
    fileName = ""
    for f in metadata['files']:
        if valid_filetype(f['name']) \
            and f['source'].lower() == 'original' \
            and 'thumb' not in f['name']:
            fileName = f['name']
            break    

    if not fileName:
        # Original wasn't an image
        for f in metadata['files']:
            if '_jp2.zip' in f['name']:
                fileName = f"{f['name']}/{f['name'].replace('.zip','')}/{f['name'].replace('jp2.zip','0000.jp2')}"

    imgId = f"{identifier}/{fileName}".replace('/','%2f')
    imgURL = f"{IMG_SRV}/3/{imgId}"
    

    thumbnail = [{
              "id": f"https://archive.org/download/{identifier}/__ia_thumb.jpg",
              "type": "Image",
              "format": "image/jpeg",
                    }]

    manifest.make_canvas_from_iiif(url=imgURL,
                                    id=f"https://iiif.archivelab.org/iiif/{identifier}/canvas",
                                    label="1",
                                    anno_page_id=f"{uri}/annotationPage/1",
                                    anno_id=f"{uri}/annotation/1", 
                                    thumbnail=thumbnail)


def addMetadata(item, identifier, metadata, collection=False):
    item.homepage = [{"id": f"https://archive.org/details/{identifier}",
                         "type": "Text",
                         "label": {"en": ["Item Page on Internet Archive"]},
                         "format": "text/html"}]

    item.provider = [{"id": "https://archive.org",
                         "type": "Agent",
                         "label": {"en": ["The Internet Archive"]}}]

    if "licenseurl" in metadata:
        item.rights = metadata["licenseurl"].replace("https", "http", 1)

    if "description" in metadata:
        item.summary = {"none": [metadata["description"]]}

    excluded_fields = [
        'avg_rating', 'backup_location', 'btih', 'description', 'downloads',
        'imagecount', 'indexflag', 'item_size', 'licenseurl', 'curation', 
        'noindex', 'num_reviews', 'oai_updatedate', 'publicdate', 'publisher',  'reviewdate',
        'scanningcentre', 'stripped_tags', 'uploader'
    ]

    manifest_metadata = []

    for field in metadata:
        if field not in excluded_fields:
            if type(metadata[field]) != list:
                metadata_value = [str(metadata[field])]
            else:
                metadata_value = metadata[field]
            manifest_metadata.append(
                {"label": {"none": [field]}, "value": {"none": metadata_value}})

    item.metadata = manifest_metadata


def create_manifest3(identifier, domain=None, page=None):
    # Get item metadata
    metadata = requests.get('%s/metadata/%s' % (ARCHIVE, identifier)).json()

    mediatype = metadata['metadata']['mediatype']

    # Used to build up URIs for the manifest
    uri = f"{domain}{identifier}"

    config.configs['helpers.auto_fields.AutoLang'].auto_lang = "none"

    manifest = Manifest(id=f"{uri}/manifest.json", label=metadata["metadata"]["title"])

    addMetadata(manifest, identifier, metadata['metadata'])

    try:
         thumbnail = [{
              "id": f"https://archive.org/download/{identifier}/__ia_thumb.jpg",
              "type": "Image",
              "format": "image/jpeg",
                                    }]
    except:
        pass


    if mediatype == 'texts':
        # Get bookreader metadata (mostly for filenames and height / width of image)
        # subprefix can be different from the identifier use the scandata filename to find the correct prefix
        # if not present fall back to identifier
        subprefix = identifier
        for fileMd in metadata['files']:
            if fileMd['name'].endswith('_scandata.xml'):
                subprefix = fileMd['name'].replace('_scandata.xml', '')

        bookReaderURL = f"https://{metadata.get('server')}/BookReader/BookReaderJSIA.php?id={identifier}&itemPath={metadata.get('dir')}&server={metadata.get('server')}&format=jsonp&subPrefix={subprefix}"

        print (f'Book reader url: {bookReaderURL}')
        bookreader = requests.get(bookReaderURL).json()
        if 'error' in bookreader:
            # Image stack not found. Maybe a single image
            singleImage(metadata, identifier, manifest, uri)
        else:
            pageCount = 0
            # In json: /29/items/goody/goody_jp2.zip convert to goody/good_jp2.zip
            zipFile = '/'.join(bookreader['data']['brOptions']['zip'].split('/')[-2:])

            for pageSpread in bookreader['data']['brOptions']['data']:
                for page in pageSpread:
                    fileUrl = urlparse(page['uri'])
                    fileName = parse_qs(fileUrl.query).get('file')[0]
                    imgId = f"{zipFile}/{fileName}".replace('/','%2f')
                    imgURL = f"{IMG_SRV}/3/{imgId}"

                    canvas = Canvas(id=f"https://iiif.archivelab.org/iiif/{identifier}${pageCount}/canvas", label=f"{page['leafNum']}", thumbnail=thumbnail)

                    body = ResourceItem(id=f"{imgURL}/full/max/0/default.jpg", type="Image")
                    body.format = "image/jpeg"
                    body.service = [ServiceItem(id=imgURL, profile="level2", type="ImageService3")]

                    annotation = Annotation(id=f"{uri}/annotation/{pageCount}", motivation='painting', body=body, target=canvas.id)

                    annotationPage = AnnotationPage(id=f"{uri}/annotationPage/{pageCount}")
                    annotationPage.add_item(annotation)

                    canvas.add_item(annotationPage)
                    canvas.set_hwd(page['height'], page['width'])

                    manifest.add_item(canvas)
                    # Create canvas from IIIF image service. Note this is very slow:
                    #canvas = manifest.make_canvas_from_iiif(url=imgURL,
                    #                            id=f"https://iiif.archivelab.org/iiif/{identifier}${pageCount}/canvas",
                    #                            label=f"{page['leafNum']}")
                    pageCount += 1
    elif mediatype == 'image':
        singleImage(metadata, identifier, manifest, uri)
    elif mediatype == 'audio' or mediatype == 'etree':
        # sort the files into originals and derivatives, splitting the derivatives into buckets based on the original
        originals = []
        derivatives = {}
        for f in metadata['files']:
            if f['source'] == 'derivative' and not isinstance(f['original'], list):
                if f['original'] in derivatives:
                    derivatives[f['original']][f['format']] = f
                else:
                    derivatives[f['original']] = {f['format']: f}
            elif f['source'] == 'original':
                originals.append(f)

        # create the canvases for each original
        for file in [f for f in originals if f['format'] in ['VBR MP3', '32Kbps MP3', '56Kbps MP3', '64Kbps MP3', '96Kbps MP3', '128Kbps MP3', 'MPEG-4 Audio', 'Flac', 'AIFF', 'Apple Lossless Audio', 'Ogg Vorbis', 'WAVE', '24bit Flac', 'Shorten']]:
            normalised_id = file['name'].rsplit(".", 1)[0]
            slugged_id = normalised_id.replace(" ", "-")
            c_id = f"https://iiif.archivelab.org/iiif/{identifier}/{slugged_id}/canvas"
            
            try:
                c = Canvas(id=c_id, label=normalised_id, duration=float(file['length']), thumbnail=thumbnail)
            except:
                c = Canvas(id=c_id, label=normalised_id, duration=float(file['length']))

            # create intermediary objects
            ap = AnnotationPage(id=f"https://iiif.archivelab.org/iiif/{identifier}/{slugged_id}/page")
            anno = Annotation(id=f"https://iiif.archivelab.org/iiif/{identifier}/{slugged_id}/annotation", motivation="painting", target=c.id)

            # create body based on whether there are derivatives or not:
            if file['name'] in derivatives:
                body = Choice(items=[])
                # add the choices in order per https://github.com/ArchiveLabs/iiif.archivelab.org/issues/77#issuecomment-1499672734
                for format in ['VBR MP3', '32Kbps MP3', '56Kbps MP3', '64Kbps MP3', '96Kbps MP3', '128Kbps MP3', 'MPEG-4 Audio', 'Flac', 'AIFF', 'Apple Lossless Audio', 'Ogg Vorbis', 'WAVE', '24bit Flac', 'Shorten']:
                    if format in derivatives[file['name']]:
                        r = ResourceItem(id=f"https://archive.org/download/{identifier}/{derivatives[file['name']][format]['name'].replace(' ', '%20')}",
                                         type='Audio',
                                         format=to_mimetype(format),
                                         label={"none": [format]},
                                         duration=float(file['length']))
                        body.items.append(r)
                    elif file['format'] == format:
                        r = ResourceItem(
                            id=f"https://archive.org/download/{identifier}/{file['name'].replace(' ', '%20')}",
                            type='Audio',
                            format=to_mimetype(format),
                            label={"none": [format]},
                            duration=float(file['length']))
                        body.items.append(r)
            else:
                # todo: deal with instances where there are no derivatives for whatever reason
                pass

            anno.body = body
            ap.add_item(anno)
            c.add_item(ap)
            manifest.add_item(c)

    elif mediatype == "movies":
        # sort the files into originals and derivatives, splitting the derivatives into buckets based on the original
        originals = []
        derivatives = {}
        for f in metadata['files']:
            if f['source'] == 'derivative':
                if f['original'] in derivatives:
                    derivatives[f['original']][f['format']] = f
                else:
                    derivatives[f['original']] = {f['format']: f}
            elif f['source'] == 'original':
                originals.append(f)
            
        # create the canvases for each original
        for file in [f for f in originals if f['format'] in ['MPEG4', 'h.264 MPEG4', '512Kb MPEG4', 'HiRes MPEG4', 'MPEG2', 'h.264', 'Matroska', 'Ogg Video', 'Ogg Theora', 'WebM', 'Windows Media', 'Cinepack']]:
            normalised_id = file['name'].rsplit(".", 1)[0]
            slugged_id = normalised_id.replace(" ", "-")
            c_id = f"https://iiif.archivelab.org/iiif/{identifier}/{slugged_id}/canvas"
            
            try:
                c = Canvas(id=c_id, label=normalised_id, duration=float(file['length']), height=int(file['height']), width=int(file['width']), 
                    thumbnail=thumbnail)
            except:
                c = Canvas(id=c_id, label=normalised_id, duration=float(file['length']), height=int(file['height']), width=int(file['width']))

            # create intermediary objects
            ap = AnnotationPage(id=f"https://iiif.archivelab.org/iiif/{identifier}/{slugged_id}/page")
            anno = Annotation(id=f"https://iiif.archivelab.org/iiif/{identifier}/{slugged_id}/annotation", motivation="painting", target=c.id)

            # create body based on whether there are derivatives or not:
            if file['name'] in derivatives:
                body = Choice(items=[])
                # add the choices in order per https://github.com/ArchiveLabs/iiif.archivelab.org/issues/77#issuecomment-1499672734
                for format in ['MPEG4', 'h.264 MPEG4', '512Kb MPEG4', 'HiRes MPEG4', 'MPEG2', 'h.264', 'Matroska', 'Ogg Video', 'Ogg Theora', 'WebM', 'Windows Media', 'Cinepack']:
                    if format in derivatives[file['name']]:
                        r = ResourceItem(id=f"https://archive.org/download/{identifier}/{derivatives[file['name']][format]['name'].replace(' ', '%20')}",
                                         type='Video',
                                         format=to_mimetype(format),
                                         label={"none": [format]},
                                         duration=float(file['length']), 
                                         height=int(file['height']),
                                         width=int(file['width']),                      
                        )
                        body.items.append(r)
                    elif file['format'] == format:
                        r = ResourceItem(
                            id=f"https://archive.org/download/{identifier}/{file['name'].replace(' ', '%20')}",
                            type='Video',
                            format=to_mimetype(format),
                            label={"none": [format]},
                            duration=float(file['length']),
                            height=int(file['height']),
                            width=int(file['width']))
                        body.items.append(r)
            else:
                # todo: deal with instances where there are no derivatives for whatever reason
                pass

            anno.body = body
            ap.add_item(anno)
            c.add_item(ap)
            manifest.add_item(c)

    else:            
        print (f'Unknown mediatype "{mediatype}"')

    return json.loads(manifest.jsonld())

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

    identifier, document = identifier.split(":", 1) if ":" in identifier else (identifier, None)

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
                         and f['source'].lower() == 'original' \
                         and 'thumb' not in f['name'] )
                itempath = os.path.join(identifier, f['name'])
            url = '%s/download/%s' % (ARCHIVE, itempath)
            print(url)
            r = requests.get(url, stream=True, allow_redirects=True)

        elif mediatype.lower() == 'texts' and leaf:
            identifierpath = "/".join([identifier, document]) if document else identifier
            url = '%s/download/%s/page/leaf%s' % (ARCHIVE, identifierpath, leaf)
            r = requests.get(url)
        if r:
            with open(path, 'wb') as rc:
                rc.writelines(r.iter_content(chunk_size=1024))

    return path, mediatype

def cantaloupe_resolver(identifier):
    """Resolves an existing Image Service identifier to what it should be with the new Cantaloupe setup"""

    leaf = None
    if "$" in identifier:
        identifier, leaf = identifier.split("$", 1)

    metadata = requests.get('%s/metadata/%s' % (ARCHIVE, identifier)).json()
    if 'dir' not in metadata:
        raise ValueError("No such valid Archive.org item identifier: %s" \
                        % identifier)

    mediatype = metadata['metadata']['mediatype'].lower()
    files = metadata['files']

    if mediatype == "image":
        # single image file - find the filename

        filename = None
        for f in files: 
            if valid_filetype(f['name']) \
                 and f['source'].lower() == 'original' \
                 and 'thumb' not in f['name']:

                filename = f['name'].replace(" ", "%20")

        if filename:
            return f"{identifier}%2f{filename}"

    elif mediatype == "texts" and leaf:
        # book - find the jp2 zip and assume the filename?
        # TODO: use one of the BookReader (or other) APIs to be 100% certain here
        filename = None
        fileIdentifier = ""
        extension = ".jp2"

        # First try the identifier then _jp2.zip
        for f in files:
            if f['name'].lower() == f'{identifier.lower()}_jp2.zip':
                filename = f['name']
                fileIdentifier = filename[:-1 * len('_jp2.zip')]

        # next look for any _jp2.zip that has a different name to the identifier 
        if not filename:
            for f in files:
                if f['name'].endswith('_jp2.zip'):
                    filename = f['name']
                    fileIdentifier = filename[:-1 * len('_jp2.zip')]
        # Prefer zip files but if not return tar
        if not filename:
            for f in files:
                if f['name'].endswith('_jp2.tar'):
                    filename = f['name']
                    fileIdentifier = filename[:-1 * len('_jp2.tar')]

        # if no jp2s look for tiffs
        if not filename:
            for f in files:
                if f['name'].endswith('_tif.zip'):
                    filename = f['name']
                    fileIdentifier = filename[:-1 * len('_tif.zip')]
                    extension = ".tif"

        #filename = next(f for f in files if f['source'].lower() == 'derivative' \
        #                and f['name'].endswith('_jp2.zip'))['name']
        if filename:
            dirpath = filename[:-4]
            filepath = f"{fileIdentifier}_{leaf.zfill(4)}{extension}"
            return f"{identifier}%2f{filename}%2f{dirpath}%2f{filepath}"

    print (f'images not found for {identifier}')    
    for f in files:
        print (f"source: {f['source'].lower()} name: {f['name']} and {f['source'].lower() == 'derivative'} {f['name'].endswith('_jp2.zip')}")
