import requests
import json
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

load_dotenv(dotenv_path='./app/prepdocs/.env')

key_vault_name = os.getenv('AZURE_KEY_VAULT')
default_credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net", credential=default_credential)
cognitive_search_url = secret_client.get_secret('AzureCognitiveSearchEndpoint').value
api_key = secret_client.get_secret('AzureCognitiveSearchKey').value


index_name = os.getenv('LINE_BOT_NAME') + os.getenv('INDEX_NAME')

request_body = {
  "fields":
  [
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": True,
      "filterable": False,
      "retrievable": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "standard.lucene",
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_content_type",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": False,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_size",
      "type": "Edm.Int64",
      "searchable": False,
      "filterable": True,
      "retrievable": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_last_modified",
      "type": "Edm.DateTimeOffset",
      "searchable": False,
      "filterable": True,
      "retrievable": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_content_md5",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": False,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_name",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_path",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": True,
      "sortable": False,
      "facetable": False,
      "key": True,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_storage_file_extension",
      "type": "Edm.String",
      "searchable": False,
      "filterable": True,
      "retrievable": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_content_encoding",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": False,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_content_type",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": False,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "metadata_language",
      "type": "Edm.String",
      "searchable": False,
      "filterable": False,
      "retrievable": False,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": None,
      "synonymMaps": []
    },
    {
      "name": "people",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": False,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "organizations",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": False,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "locations",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": False,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "keyphrases",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": False,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "language",
      "type": "Edm.String",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": True,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "standard.lucene",
      "synonymMaps": []
    },
    {
      "name": "merged_content",
      "type": "Edm.String",
      "searchable": True,
      "filterable": False,
      "retrievable": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "text",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": False,
      "retrievable": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "layoutText",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": False,
      "retrievable": True,
      "sortable": False,
      "facetable": False,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "ja.microsoft",
      "synonymMaps": []
    },
    {
      "name": "imageTags",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": False,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "standard.lucene",
      "synonymMaps": []
    },
    {
      "name": "imageCaption",
      "type": "Collection(Edm.String)",
      "searchable": True,
      "filterable": True,
      "retrievable": True,
      "sortable": False,
      "facetable": True,
      "key": False,
      "indexAnalyzer": None,
      "searchAnalyzer": None,
      "analyzer": "standard.lucene",
      "synonymMaps": []
    }
  ]
}

headers = { "api-key " : api_key, "Content-Type" : "application/json" }
ret = requests.put(cognitive_search_url + f"indexes/{index_name}?api-version=2020-06-30", headers=headers, data=json.dumps(request_body))
