import unittest
from flask.testing import FlaskClient
from iiify.app import app

class TestManifests(unittest.TestCase):

    def setUp(self) -> None:
        self.test_app = FlaskClient(app)

    def test_v3_image_manifest(self):
        resp = self.test_app.get("/iiif/3/rashodgson68/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json

        self.assertEqual(manifest['type'], "Manifest", f"Unexpected type. Expected Manifest go {manifest['type']}")
        self.assertEqual(len(manifest['items']),32,f"Expected 32 canvases but got: {len(manifest['items'])}")

    def test_v3_single_image_manifest(self):
        resp = self.test_app.get("/iiif/3/img-8664_202009/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json

        self.assertEqual(manifest['type'], "Manifest", f"Unexpected type. Expected Manifest go {manifest['type']}")
        self.assertEqual(len(manifest['items']),1,f"Expected 1 canvas but got: {len(manifest['items'])}")

    def test_v3_single_text_manifest(self):
        resp = self.test_app.get("/iiif/3/fbf_3chords_1_/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json

        self.assertEqual(manifest['type'], "Manifest", f"Unexpected type. Expected Manifest go {manifest['type']}")
        self.assertEqual(len(manifest['items']),1,f"Expected 1 canvas but got: {len(manifest['items'])}")


    def test_v3_vermont_Life_Magazine(self):
        resp = self.test_app.get("/iiif/3/rbmsbk_ap2-v4_2001_V55N4/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json

        self.assertEqual(len(manifest['items']),116,f"Expected 116 canvas but got: {len(manifest['items'])}")

    def test_v3_single_video_manifest(self):
        resp = self.test_app.get("/iiif/3/youtube-7w8F2Xi3vFw/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json

        self.assertEqual(len(manifest['items']),1,f"Expected 1 canvas but got: {len(manifest['items'])}")

    #logic to cover etree mediatype github issue #123
    def test_v3_etree_mediatype(self):
        resp = self.test_app.get("/iiif/3/gd72-04-14.aud.vernon.23662.sbeok.shnf/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json

        self.assertEqual(len(manifest['items']),36,f"Expected 36 canvases but got: {len(manifest['items'])}")


    def test_v3_64Kbps_MP3(self):
        resp = self.test_app.get("/iiif/3/TvQuran.com__Alafasi/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json
        self.assertEqual(len(manifest['items']),114,f"Expected 114 canvases but got: {len(manifest['items'])}")
        self.assertEqual("64Kbps MP3".lower() in resp.text.lower(), True, f"Expected the string '64Kbps MP3'")


    def test_v3_128Kbps_MP3(self):
        resp = self.test_app.get("/iiif/3/alice_in_wonderland_librivox/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json
        self.assertEqual(len(manifest['items']),12,f"Expected 12 canvases but got: {len(manifest['items'])}")
        self.assertEqual("128kbps mp3".lower() in resp.text.lower(), True, f"Expected the string '128kbps mp3'")

    def test_v3_h264_MPEG4_OGG_Theora(self):
        resp = self.test_app.get("/iiif/3/taboca_201002_03/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json
        self.assertEqual(len(manifest['items']),251,f"Expected 251 canvases but got: {len(manifest['items'])}")
        self.assertEqual("h.264 MPEG4".lower() in resp.text.lower(), True, f"Expected the string 'h.264 MPEG4'")
        self.assertEqual("OGG Theora".lower() in resp.text.lower(), True, f"Expected the string 'OGG Theora'")

    def test_v3_aiff(self):
        resp = self.test_app.get("/iiif/3/PDextend_AIFF/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json
        self.assertEqual(len(manifest['items']),38,f"Expected 38 canvases but got: {len(manifest['items'])}")
        self.assertEqual("AIFF".lower() in resp.text.lower(), True, f"Expected the string 'AIFF'")

    #Test for single quotes in item filenames
    def test_v3_single_quote_filename(self):
        resp = self.test_app.get("/iiif/3/acap-test/manifest.json")
        self.assertEqual(resp.status_code, 200)
        manifest = resp.json
        self.assertEqual(len(manifest['items']),5,f"Expected 5 canvases but got: {len(manifest['items'])}")
        self.assertEqual(manifest['items'][0]['items'][0]['items'][0]['body']['items'][0]['id'], "https://archive.org/download/acap-test/After%20I%20Say%20I%27m%20Sorry%3F%20-%20Miss%20Betty%20Morgan.mp3",
            f"Expected a URL-encoded string but got {manifest['items'][0]['items'][0]['items'][0]['body']['items'][0]['id']} instead")

''' to test:
kaled_jalil (no derivatives)
Dokku_obrash (geo-restricted?)
m4a filetypes (No length to files?)
78_mr-sandman_the-chordettes-archie-bleyer-pat-ballard-archie-ballard_gbia0017988b (audio file with auto-generated VTT)
'''

if __name__ == '__main__':
    unittest.main()