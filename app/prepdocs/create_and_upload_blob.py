# https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-blob-upload-python

import re, os
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from pdfminer.high_level import extract_text # 日本語対応テキスト抽出ライブラリ
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.keyvault.secrets import SecretClient

load_dotenv(dotenv_path='./app/prepdocs/.env')

def check_container_existence(blob_service_client, container_name):
    container_client = blob_service_client.get_container_client(container_name)
    
    try:
        container_properties = container_client.get_container_properties()
        return True  # コンテナーが存在する場合
    except:
        return False

def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

def remove_newline(text: str) -> str:
    text = text.replace('\r\n', '')
    text = text.replace('\n', '')
    return text

def remove_space(text: str) -> str:
    text = text.replace(' ', '')
    return text

def remove_cid_tags(input_string: str) -> str:
    cleaned_string = re.sub(r'\(cid:\d+\)', '', input_string)
    return cleaned_string

def is_japanese(str):
    return True if re.search(r'[ぁ-んァ-ン]', str) else False 

key_vault_name = os.getenv('AZURE_KEY_VAULT')
default_credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net", credential=default_credential)
storage_account = secret_client.get_secret('AzureStorageAccountName')
storage_account_name = storage_account.value
account_url = f"https://{storage_account_name}.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url, credential=default_credential)

container_name = os.getenv('LINE_BOT_NAME') + os.getenv('BLOB_CONTAINER_NAME')

exists = check_container_existence(blob_service_client, container_name)

#アップロードするファイルが格納されたパス・ファイル名
local_path="./data"
local_file_name = os.getenv('LOCAL_FILE_NAME')
upload_file_path = local_path + "/" + local_file_name

if not exists:
    blob_service_client.create_container(container_name)

text = extract_text_from_pdf(upload_file_path)
pages = text.split('\x0c')

# セパレータで分割して、文字数でマージするTextSplitter
text_splitter = CharacterTextSplitter(
    separator = "。",
    chunk_size = 200,
    chunk_overlap = 0,
)

for page_num, page_text in enumerate(pages, start=1):
    splited_page_text = text_splitter.split_text(page_text)
    for idx, data in enumerate(splited_page_text):
        data = remove_newline(data)
        data = remove_space(data)
        data = remove_cid_tags(data)
        if data.endswith("・・"): continue # エラー回避
        if not is_japanese(data): continue # 日本語以外は無視
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name + "_" + str(page_num) + "_" + str(idx) + ".txt")
        blob_client.upload_blob(data, overwrite=True)
