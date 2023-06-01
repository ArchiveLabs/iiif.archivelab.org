import unittest
from flask.testing import FlaskClient
from iiify.app import app

class TestCollections(unittest.TestCase):

    def setUp(self) -> None:
        self.test_app = FlaskClient(app)

    def test_v3_collection(self):
        resp = self.test_app.get("/iiif/3/frankbford/collection.json")
        self.assertEqual(resp.status_code, 200)
        collection = resp.json

        self.assertEqual(collection['type'], "Collection", f"Unexpected type. Expected collection got {collection['type']}")
        self.assertEqual(len(collection['items']),1001,f"Expected 1000 items but got: {len(collection['items'])}")
        self.assertEqual(collection['items'][-1]['type'],'Collection',"Expected last item to be a collection pointing to the next set of results")


if __name__ == '__main__':
    unittest.main()