import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./app/prepdocs/.env')

cognitive_search_url = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
api_key = os.getenv('AZURE_COGNITIVE_SEARCH_KEY')

indexer_name = os.getenv('LINE_BOT_NAME') + os.getenv('INDEXER_NAME')
datasource_name = os.getenv('LINE_BOT_NAME') + os.getenv('DATASOURCE_NAME')
index_name = os.getenv('LINE_BOT_NAME') + os.getenv('INDEX_NAME')
skillset_name = os.getenv('LINE_BOT_NAME') + os.getenv('SKILLSET_NAME')

request_body = {
  "name": indexer_name,
  "description": "",
  "dataSourceName" : datasource_name,
  "targetIndexName" : index_name,
  "skillsetName" : skillset_name,
  "fieldMappings" : [
    {
      "sourceFieldName": "metadata_storage_path",
      "targetFieldName": "metadata_storage_path",
      "mappingFunction": {
        "name": "base64Encode",
        "parameters": None
      }
    }
  ],
  "outputFieldMappings" :
  [
    {
      "sourceFieldName": "/document/merged_content/people",
      "targetFieldName": "people"
    },
    {
      "sourceFieldName": "/document/merged_content/organizations",
      "targetFieldName": "organizations"
    },
    {
      "sourceFieldName": "/document/merged_content/locations",
      "targetFieldName": "locations"
    },
    {
      "sourceFieldName": "/document/merged_content/keyphrases",
      "targetFieldName": "keyphrases"
    },
    {
      "sourceFieldName": "/document/language",
      "targetFieldName": "language"
    },
    {
      "sourceFieldName": "/document/merged_content",
      "targetFieldName": "merged_content"
    },
    {
      "sourceFieldName": "/document/normalized_images/*/text",
      "targetFieldName": "text"
    },
    {
      "sourceFieldName": "/document/normalized_images/*/layoutText",
      "targetFieldName": "layoutText"
    },
    {
      "sourceFieldName": "/document/normalized_images/*/imageTags/*/name",
      "targetFieldName": "imageTags"
    },
    {
      "sourceFieldName": "/document/normalized_images/*/imageCaption",
      "targetFieldName": "imageCaption"
    }
  ],
  "parameters":
  {
    "maxFailedItems":0,
    "maxFailedItemsPerBatch":0,
    "configuration":
    {
      "dataToExtract": "contentAndMetadata",
      "parsingMode": "default",
      "imageAction": "generateNormalizedImages"
    }
  }
}

headers = { "api-key " : api_key, "Content-Type" : "application/json" }
ret = requests.put(cognitive_search_url + f"/indexers/{indexer_name}?api-version=2020-06-30", headers=headers, data=json.dumps(request_body))

print(ret)

