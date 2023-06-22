import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR) + "/..")

from iiify.resolver import cantaloupe_resolver

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ('Usage:\n\tconvertURLs.py [access_log]')
        exit(-1)

    VERBS = ["GET", "HEAD", "OPTIONS"]
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
                                newID = cantaloupe_resolver(identifier)
                                newUrl = ""
                                
                                for i in range(len(urlSplit)):
                                    if i == 1:
                                        newUrl += "iiif/2"
                                    elif i == 2:    
                                        newUrl += newID
                                    else:
                                        newUrl += urlSplit[i]
                                    if i != len(urlSplit) - 1:
                                        newUrl += '/'        

                                #print (f"{verb} {newUrl}")
                                print (f"https://services-ia-iiif-cantaloupe-experiment.dev.archive.org/iiif/2/{newID}/info.json")