import os
import sys
from urllib.request import urlopen
from urllib.error import HTTPError
import json

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print ('Usage:\n\turlCheck.py [access_log]')
        exit(-1)

    dir = "info.json"
    if not os.path.exists(dir):
        # If it doesn't exist, create it
        os.makedirs(dir)

    with open(sys.argv[1]) as f:
        for line in f:
            if not os.path.exists(f"{dir}/{line.split('/')[5]}.json"):
                try:
                    response = urlopen(line)
                    if response.getcode() != 200: 
                        print (f"{connection.getcode()}: {line}")    
                    else:
                        data = json.loads(response.read())    
                        filename = data['@id'].split("/")[-1:][0]

                        with open(f"{dir}/{filename}.json", "w") as f:
                            json.dump(data, f, indent=4)

                    response.close()
                except HTTPError as e:
                    print (f"{e.getcode()}: {line}")    