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

if __name__ == '__main__':
    unittest.main()