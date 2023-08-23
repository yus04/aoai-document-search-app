import os, requests, json, logging, openai, datetime, uuid
from flask import (Flask, request, session, abort)
from datetime import timedelta
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from azure.cosmos import CosmosClient

load_dotenv(dotenv_path='.env')
# load_dotenv(dotenv_path='./app/backend/.env') # for local test

openai.api_type = "azure"
openai.api_version = "2023-05-15"
# openai.api_base = os.getenv('OPENAI_API_BASE')
openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
# openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = os.getenv('AZURE_OPENAI_KEY')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_APP_SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# search_document_key = os.getenv('SEARCH_DOCUMENT_KEY', None)
search_document_key = os.getenv('AZURE_COGNITIVE_SEARCH_KEY', None)

# pdf_path = "data/PRIUS_UG_JP_M47E40_1_2301.pdf"

@app.route("/")
def index():
    return "index"

@app.route("/callback", methods=['POST'])
def callback():
    init()
    signature = request.headers['x-line-signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    answer, top_results, file_names = get_answer(event.message.text)
    top_results_str = top_results_to_str(top_results, file_names, True)
    answer_and_citation = "【AIによる回答】\n" + answer + "\n\n" + "【取扱説明書の抜粋】\n" + top_results_str
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=answer_and_citation)
    )
    insert_cosmos_db(event.source.user_id, event.message.text, answer_and_citation)

def get_question() -> str:
    question=request.args['question']
    return question

def get_answer(question: str) -> [str, str]:
    query = generate_query(question)
    search_result, top_results, file_names = search_document(query)
    answer = generate_answer(question, search_result)
    add_chat_history(question, answer)
    return answer, top_results, file_names

def init():
    if "chat_history" not in session:
        logging.info('chat_history is not in session.')
        session['chat_history'] = []

# プロンプトの書き方の見直し
# プロンプトテンプレートの作成
def generate_query(question: str) -> str:
    logging.info('called generate_query function.')
    prompt = [
        {"role":"system","content":"検索キーワードを5つ以下で生成してください。ただし、最も重要なキーワードを1つだけ\"\"で囲って出力して下さい。"},
        {"role":"user","content":"車両が故障したときはどうすればいいですか？"},
        {"role":"assistant","content":"車両 \"故障\" 対応方法"},
    ]
    null_chat_history = []
    question = [{"role": "user", "content": question}]
    query = ask_gpt3(prompt, null_chat_history, question)
    return query

def generate_answer(question: str, search_result: str) -> str:
    logging.info('called generate_answer function.')
    prompt = [
        {"role":"system","content":"質問と質問に回答するための情報が与えられるので、文章を丁寧な表現で100文字程度でまとめてください。"},
        {"role":"user","content":"質問内容：前方カメラの注意事項 質問に回答するための情報：前方カメラの視界をさえぎらないようにする 前方カメラに強い衝撃を加えない 前方カメラの取り付け位置や向きを変更したり、取りはずしたりしない付着した場合は、取り除いてください。\
         フロントウインドウガラスにガラスコーティング剤を使用していても、前方カメラ前部に水滴などが付着した場合は、ワイパーでふき取ってください。\
         フロントウインドウガラス内側の前方カメラ取り付け部が汚れた場合は、トヨタ販売店にご相談ください。"},
        {"role":"assistant","content":"前方カメラの視界を確保するため、カメラ位置と向きを変えず、付着物を取り除きましょう。水滴がついた場合はワイパーで拭き、汚れたらトヨタ販売店に相談してください。衝撃も避けてください。"},
    ]
    question_and_search_result = [
        {"role": "user", "content": f"質問内容：{question}質問に回答するための情報：{search_result}"},
    ]
    answer = ask_gpt3(prompt, session["chat_history"], question_and_search_result)
    return answer

def ask_gpt3(prompt: [], chat_history: [], question: []) -> str:
    logging.info('called ask_gpt3 function.')
    messages = []
    for item in prompt: messages.append(item)
    for item in chat_history: messages.append(item)
    for item in question: messages.append(item)
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=messages,
    )
    answer = response['choices'][0]['message']['content']
    return answer

def search_document(query: str) -> [str, [str], [str]]:
    # urlそのままはよくない
    cognitive_search_url = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
    cognitive_search_url = remove_trailing_slash(cognitive_search_url)
    index_name = os.getenv('INDEX_NAME')
    # url_to_get = f"https://search-service-yzdsredleanja.search.windows.net/indexes/azureblob-index8/docs?api-version=2023-07-01-Preview&search={query}"
    url_to_get = f"{cognitive_search_url}/indexes/{index_name}/docs?api-version=2023-07-01-Preview&search={query}"
    custom_headers = { "api-key": search_document_key }
    responseText = send_get_request_with_headers(url_to_get, custom_headers)
    responseJson = decode_unicode_escape(responseText)
    top_results, file_names = select_top_results(responseJson, 3)
    top_results_str = top_results_to_str(top_results, [], False)
    search_results = top_results_str
    return search_results, top_results, file_names

def remove_trailing_slash(url):
    if url.endswith('/'):
        url = url[:-1]
    return url

def send_get_request_with_headers(url: str, headers: json) -> str:
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Request successful!")
            return response.text
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def decode_unicode_escape(responseText: str) -> json:
    responseJson = json.loads(responseText)
    return json.dumps(responseJson, ensure_ascii=False)

def select_top_results(responseJson: json, count: int) -> [[str], [str]]:
    responseJson = json.loads(responseJson)
    top_results = []
    file_names = []
    for item in responseJson['value']:
        top_results.append(item['content'])
        file_names.append(item['metadata_storage_name'])
    return top_results[:count], file_names[:count]

def top_results_to_str(top_results: [], file_names: [], shaping: bool) -> str:
    top_results_str = ""
    for idx, top_result in enumerate(top_results):
        if shaping: top_results_str += "・"
        if len(top_results) == len(file_names):
            top_results_str += get_page(file_names[idx])
        top_results_str += top_result
        if shaping: top_results_str += "\n"
    return top_results_str.rstrip()

def get_page(file_name: str) -> str:
    return "(p. " + file_name.split('_')[0] + "に記載)"

def add_chat_history(question: str, answer: str) -> None:
    session.permanent = True
    session['chat_history'].append({"role": "user", "content": question})
    session['chat_history'].append({"role": "assistant", "content": answer})

def insert_cosmos_db(user_id: str, input_txt: str, output_txt: str) -> None:
    try:
        connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING', None)
        cosmos_db_name = os.getenv('COSMOS_DB_NAME', None)
        cosmos_container_name = os.getenv('COSMOS_DB_CONTAINER_NAME', None)
        client = CosmosClient.from_connection_string(connection_string)
        database_client = client.get_database_client(cosmos_db_name)
        container_client = database_client.get_container_client(cosmos_container_name)
        dt_now_jst_aware = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        container_client.upsert_item({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'question': str(input_txt),
                'answer': str(output_txt),
                'created_at': str(dt_now_jst_aware),
        })
        logging.info('Project details are stored to Cosmos DB.')
    except Exception as e:
        logging.error(e)

# Test Function
# Attention: Need to provide question as a parameter
# for example, <URL>?question=車両が故障したときはどうすればいいですか？
@app.route("/test_get_answer")
def test_get_answer():
    init()
    question = get_question()
    query = generate_query(question)
    search_result, _, _ = search_document(query)
    answer = generate_answer(question, search_result)
    add_chat_history(question, answer)
    return answer

@app.route("/test_insert_cosmos_db")
def test_insert_cosmos_db():
    user_id = "test_user_id"
    input_txt = "test_input_txt"
    output_txt = "test_output_txt"
    insert_cosmos_db(user_id, input_txt, output_txt)
    return "inserted"

if __name__ == '__main__':
   app.run(port=80)
