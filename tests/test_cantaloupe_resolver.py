import unittest
from iiify.resolver import cantaloupe_resolver

class TestCantaloupeResolver(unittest.TestCase):

    def test_single_image(self):
        cid = cantaloupe_resolver("img-8664_202009")
        self.assertEqual(cid, "img-8664_202009%2fIMG_8664.jpg")

    def test_multiple_images(self):
        cid = cantaloupe_resolver("wg35-2-388$0")
        self.assertEqual(cid, "wg35-2-388%2fwg35-2-388_jp2.zip%2fwg35-2-388_jp2%2fwg35-2-388_0000.jp2")
        cid = cantaloupe_resolver("wg35-2-388$1")
        self.assertEqual(cid, "wg35-2-388%2fwg35-2-388_jp2.zip%2fwg35-2-388_jp2%2fwg35-2-388_0001.jp2")


if __name__ == '__main__':
    unittest.main()