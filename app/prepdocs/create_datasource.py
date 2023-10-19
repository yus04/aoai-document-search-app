# https://learn.microsoft.com/ja-jp/rest/api/searchservice/create-data-source
# API version: 2020-06-30

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

cognitive_search = secret_client.get_secret('AzureCognitiveSearchEndpoint')
cognitive_search_url = cognitive_search.value
api_key = secret_client.get_secret('AzureCognitiveSearchKey')
api_key_value = api_key.value

storage_account = secret_client.get_secret('AzureStorageAccountName').value
account_key = secret_client.get_secret('AzureStorageAccountKey').value


datasource_name = os.getenv('LINE_BOT_NAME') + os.getenv('DATASOURCE_NAME')
container_name = os.getenv('LINE_BOT_NAME') + os.getenv('BLOB_CONTAINER_NAME')

request_body = {
    "name" : datasource_name,
    "description" : "",
    "type" : "azureblob",
    "credentials" :
    { "connectionString" :
        f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={account_key};EndpointSuffix=core.windows.net"
    },
    "container" : { "name" : container_name }
}

headers = { "api-key " : api_key_value, "Content-Type" : "application/json" }
ret = requests.post(cognitive_search_url + "datasources?api-version=2020-06-30", headers=headers, data=json.dumps(request_body))
