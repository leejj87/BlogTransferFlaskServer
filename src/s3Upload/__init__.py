import os
import json
BASEFILE_LOCATION=os.path.dirname(os.path.abspath(__file__))
init_jsonFile=os.path.join(BASEFILE_LOCATION,"init.json")
with open(init_jsonFile,'r') as f:
    json_diction=json.loads(f.read())
AWS_ACCESS_KEY_ID = json_diction['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = json_diction['AWS_SECRET_ACCESS_KEY']
AWS_DEFAULT_REGION = json_diction['AWS_DEFAULT_REGION']
AWS_BUCKET_NAME = json_diction['AWS_BUCKET_NAME']
CORES=json_diction['CORES']