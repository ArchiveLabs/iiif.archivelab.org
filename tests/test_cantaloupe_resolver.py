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

    def test_original_zip(self):
        """This is a multipage item with a zip file of jp2s
        """
        cid = cantaloupe_resolver("pennsylvaniavege14penn$1")
        self.assertEqual(cid, "pennsylvaniavege14penn%2fpennsylvaniavege14penn_jp2.zip%2fpennsylvaniavege14penn_jp2%2fpennsylvaniavege14penn_0001.jp2")

    def test_tar(self):
        """This item only has a tar file no zip
        """
        cid = cantaloupe_resolver("mobot31753002307400$1")
        self.assertEqual(cid, "mobot31753002307400%2fmobot31753002307400_jp2.tar%2fmobot31753002307400_jp2%2fmobot31753002307400_0001.jp2")

    def test_problem_image(self):
        """This image is a tiff
        """
        cid = cantaloupe_resolver("opencontext-10-1998fig2tr52late-wall-west-face")
        self.assertEqual(cid, "opencontext-10-1998fig2tr52late-wall-west-face%2f10-1998fig2tr52late-wall-west-face.tiff")

    def test_zip_and_tar(self):
        """This item has both a _jp2.zip and a _jp2.tar. The zip should be preferred 
        """
        cid = cantaloupe_resolver("v52n2gullv52ngold$1")
        self.assertEqual(cid, "v52n2gullv52ngold%2fv52n2gullv52ngold_jp2.zip%2fv52n2gullv52ngold_jp2%2fv52n2gullv52ngold_0001.jp2")

    def test_tif_zip(self):
        """This item only has a _tiff.zip so it should be used. The extension should be a tif not jp2
        """
        cid = cantaloupe_resolver("erzhlungen00kleigoog$9")
        self.assertEqual(cid, "erzhlungen00kleigoog%2ferzhlungen00kleigoog_tif.zip%2ferzhlungen00kleigoog_tif%2ferzhlungen00kleigoog_0009.tif")

    def test_with_raw(self):
        """In this example it has both a _jp2.zip and a raw_jp2.zip. The raw file doesn't work
        """
        cid = cantaloupe_resolver("1994harlequinducksurreicrich$1")
        self.assertEqual(cid, "1994harlequinducksurreicrich%2f1994harlequinducksurreicrich_jp2.zip%2f1994harlequinducksurreicrich_jp2%2f1994harlequinducksurreicrich_0001.jp2")

    def test_with_uppercase(self):
        """It looks like in this case the identifier is upper case in the zipfie and filename of the image
            CAT31108226_jp2/CAT31108226_0000.jp2	jpg	2014-10-16 10:57	485693
            CAT31108226_jp2/CAT31108226_0001.jp2	jpg	2014-10-16 10:57	264503
            CAT31108226_jp2/CAT31108226_0002.jp2	jpg	2014-10-16 10:58	298541
        """
        cid = cantaloupe_resolver("CAT31108226$1")
        self.assertEqual(cid, "CAT31108226%2fCAT31108226_jp2.zip%2fCAT31108226_jp2%2fCAT31108226_0001.jp2")

    def test_with_lowercase(self):
        """It looks like in this case the identifier is lower case in the zipfie and filename of the image
            cat31151811_jp2/cat31151811_0000.jp2	jpg	2015-12-31 21:04	123361
            cat31151811_jp2/cat31151811_0001.jp2	jpg	2015-12-31 21:04	1621954
            cat31151811_jp2/cat31151811_0002.jp2	jpg	2015-12-31 21:04	1124782
            cat31151811_jp2/cat31151811_0003.jp2
        """
        cid = cantaloupe_resolver("CAT31151811$1")
        self.assertEqual(cid, "CAT31151811%2fcat31151811_jp2.zip%2fcat31151811_jp2%2fcat31151811_0001.jp2")

    def test_single_image_issue(self):
        """This creates a broken image in cantaloupe. I think its a image problem rather than a resolution issue. 
        """
        cid = cantaloupe_resolver("opencontext-22-e-2-203-4-1-p-3jpg")
        self.assertEqual(cid, "opencontext-22-e-2-203-4-1-p-3jpg%2f22-e-2-203-4-1-p-3jpg.JPG")

    def test_multi_case(self):
        """A big mix of upper case and lower case. Identifier is lower by filenames are mixed case
        """
        cid = cantaloupe_resolver("footmouthdisease00reyn$1")
        self.assertEqual(cid, "footmouthdisease00reyn%2fFootAndMouthDisease-The1967OutbreakAndItsAftermath_jp2.zip%2fFootAndMouthDisease-The1967OutbreakAndItsAftermath_jp2%2fFootAndMouthDisease-The1967OutbreakAndItsAftermath_0001.jp2") 

    def test_space_in_filename(self):
        cid = cantaloupe_resolver("drug-use-and-abuse-collection-of-pamphlets")
        self.assertEqual(cid, "drug-use-and-abuse-collection-of-pamphlets%2fDrug%20Use%20and%20Abuse%20(Collection%20of%20Pamphlets).jpg")

    def test_multiple_zips(self):
        cid = cantaloupe_resolver("engflowergarden00robirich$1")
        self.assertEqual(cid, "engflowergarden00robirich%2fengflowergarden00robirich_jp2.zip%2fengflowergarden00robirich_jp2%2fengflowergarden00robirich_0001.jp2")    
        
if __name__ == '__main__':
    unittest.main()