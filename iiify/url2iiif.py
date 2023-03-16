import os
import hashlib
import requests
import tempfile
import mimetypes
import internetarchive as ia
from .configs import s3key, s3secret, iiif_domain

BUF_SIZE = 65536  # 64kb
SIZE_LIMIT_MB = 200
PATH = '/2/url2iiif'
URL2IIIF_ITEMNAME = 'url2iiif'

def ia_item_exists(itemname):
    """Use IA tool to check whether itemname exists"""
    try:
        r = requests.get('https://archive.org/metadata/%s' % itemname)
        if 'metadata' in r.json():
            return True
        return False
    except Exception as e:
        print(e)
        return False

def download_file(url, path=PATH):
    filepath = '%s/%s' % (path, url.split('/')[-1])
    r = requests.get(url, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    return filepath


def get_filehash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hasher.update(data)
        return hasher.hexdigest()

def url2ia(url):
    """Creates an archive.org item for """
    hr = requests.head(url)
    if not 'image/' in hr.headers['Content-Type']:
        raise ValueError(
            'Service only works with urls with clearly '
            'identifiable images (e.g. ending in .png, .jpg, .gif, etc.')

    print(hr.headers['Content-Length'])
    if (int(hr.headers['Content-Length']) / 1000000.) > SIZE_LIMIT_MB:
        raise IOError('File size exceeds %smb' % SIZE_LIMIT_MB)

    filepath = download_file(url, path=PATH)
    filehash = get_filehash(filepath)
    filepath2 = os.path.join(PATH, filehash)
    os.rename(filepath, filepath2)

    ia.upload(URL2IIIF_ITEMNAME, filepath2, access_key=s3key, secret_key=s3secret)
    return filehash

if __name__ == "__main__":
    pass
