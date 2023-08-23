# https://learn.microsoft.com/ja-jp/rest/api/searchservice/create-data-source
# API version: 2020-06-30

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./app/prepdocs/.env')

cognitive_search_url = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
api_key = os.getenv('AZURE_COGNITIVE_SEARCH_KEY')

storage_account = os.getenv('AZURE_STORAGE_ACCOUNT')
account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')

request_body = {
    "name" : os.getenv('DATASOURCE_NAME'),
    "description" : "",
    "type" : "azureblob",
    "credentials" :
    { "connectionString" :
        f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={account_key};EndpointSuffix=core.windows.net"
    },
    "container" : { "name" : os.getenv('BLOB_CONTAINER_NAME') }
}

headers = { "api-key " : api_key, "Content-Type" : "application/json" }
ret = requests.post(cognitive_search_url + "/datasources?api-version=2020-06-30", headers=headers, data=json.dumps(request_body))

print(ret)
