import os
import sys
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/..")

from iiify.resolver import cantaloupe_resolver

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ('Usage:\n\tconvertURLs.py [access_log]')
        exit(-1)

    VERBS = ["GET", "HEAD", "OPTIONS"]
    imgList = []
    with open(sys.argv[1]) as f:
        for line in f:
            if 'info.json' in line or '.jpg' in line:
                if "url2iiif" not in line:
                    for verb in VERBS:
                        if verb in line:
                            url = line.split(f"{verb} ")[1].split(" ")[0]

                            urlSplit = url.split("/")
                            if len(urlSplit) > 3:
                                identifier = urlSplit[2].replace("%24", "$")
                                # Only add unique ids 
                                if identifier not in imgList:
                                    newID = cantaloupe_resolver(identifier)

                                    #print (f"{verb} {newUrl}")
                                    print (f"/iiif/{random.randint(2,3)}/{newID}/info.json")
                                    imgList.append(identifier)