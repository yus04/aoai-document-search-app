import os, requests, json, logging, openai, datetime, uuid, re
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from azure.cosmos import CosmosClient

load_dotenv(dotenv_path='.env')
# load_dotenv(dotenv_path='./app/backend/.env') # for local test

openai.api_type = "azure"
openai.api_version = "2023-05-15"
openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
openai.api_key = os.getenv('AZURE_OPENAI_KEY')

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_APP_SECRET_KEY')

search_document_key = os.getenv('AZURE_COGNITIVE_SEARCH_KEY', None)

conversation_style_dict = {
    'simple': '会話のスタイルを簡潔な返信に変更',
    'normal': '会話のスタイルを普通の返信に変更',
    'strict': '会話のスタイルを厳密な返信に変更'
}

authentication_credentials = {
    'priusbot' : {
        'line_channel_secret' : os.getenv('PR_LINE_CHANNEL_SECRET', None),
        'line_channel_access_token' : os.getenv('PR_LINE_CHANNEL_ACCESS_TOKEN', None),
        'line_bot_api' : LineBotApi(os.getenv('PR_LINE_CHANNEL_ACCESS_TOKEN', None)),
        'handler' : WebhookHandler(os.getenv('PR_LINE_CHANNEL_SECRET', None))
    },
    'skylinebot' : {
        'line_channel_secret' : os.getenv('SK_LINE_CHANNEL_SECRET', None),
        'line_channel_access_token' : os.getenv('SK_LINE_CHANNEL_ACCESS_TOKEN', None),
        'line_bot_api' : LineBotApi(os.getenv('SK_LINE_CHANNEL_ACCESS_TOKEN', None)),
        'handler' : WebhookHandler(os.getenv('SK_LINE_CHANNEL_SECRET', None))
    },
    'ekcrossbot' : {
        'line_channel_secret' : os.getenv('EK_LINE_CHANNEL_SECRET', None),
        'line_channel_access_token' : os.getenv('EK_LINE_CHANNEL_ACCESS_TOKEN', None),
        'line_bot_api' : LineBotApi(os.getenv('EK_LINE_CHANNEL_ACCESS_TOKEN', None)),
        'handler' : WebhookHandler(os.getenv('EK_LINE_CHANNEL_SECRET', None))
    },
    'laviebot' : {
        'line_channel_secret' : os.getenv('LA_LINE_CHANNEL_SECRET', None),
        'line_channel_access_token' : os.getenv('LA_LINE_CHANNEL_ACCESS_TOKEN', None),
        'line_bot_api' : LineBotApi(os.getenv('LA_LINE_CHANNEL_ACCESS_TOKEN', None)),
        'handler' : WebhookHandler(os.getenv('LA_LINE_CHANNEL_SECRET', None))
    }
}

pr_line_bot_api = authentication_credentials['priusbot']['line_bot_api']
sk_line_bot_api = authentication_credentials['skylinebot']['line_bot_api']
ek_line_bot_api = authentication_credentials['ekcrossbot']['line_bot_api']
la_line_bot_api = authentication_credentials['laviebot']['line_bot_api']
pr_handler = authentication_credentials['priusbot']['handler']
sk_handler = authentication_credentials['skylinebot']['handler']
ek_handler = authentication_credentials['ekcrossbot']['handler']
la_handler = authentication_credentials['laviebot']['handler']

use_bing_search = True
use_keyword_query = False

bing_api_subscription_key = os.getenv('BING_API_KEY', None)
bing_url = os.getenv('BING_ENDPOINT', None)

@app.route("/")
def index():
    return "index"

# query parameter: bot_name
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['x-line-signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    bot_name = get_bot_name()
    try:
        if bot_name == 'priusbot':
            pr_handler.handle(body, signature)
        elif bot_name == 'skylinebot':
            sk_handler.handle(body, signature)
        elif bot_name == 'ekcrossbot':
            ek_handler.handle(body, signature)
        elif bot_name == 'laviebot':
            la_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@pr_handler.add(MessageEvent, message=TextMessage)
def pr_message(event):
    handle_message(event, pr_line_bot_api, 'priusbot')

@sk_handler.add(MessageEvent, message=TextMessage)
def sk_message(event):
    handle_message(event, sk_line_bot_api, 'skylinebot')

@ek_handler.add(MessageEvent, message=TextMessage)
def ek_message(event):
    handle_message(event, ek_line_bot_api, 'ekcrossbot')

@la_handler.add(MessageEvent, message=TextMessage)
def la_message(event):
    handle_message(event, la_line_bot_api, 'laviebot')

def handle_message(event: any, line_bot_api: any, bot_name: str) -> None:
    user_message = event.message.text
    user_id = event.source.user_id
    session = read_session_from_cosmos_db(user_id)
    if is_change_conversation_style_text(user_message):
        conversation_style = change_conversation_style(user_message, user_id)
        inform_change_to_line(event.reply_token, line_bot_api, conversation_style)
    else:
        answer, top_results, file_names = get_answer(user_message, bot_name, session)
        top_results_str = top_results_to_str(top_results, file_names[:3], True)
        reply_answer_to_line(answer, top_results_str, event.reply_token, line_bot_api, session)
        insert_cosmos_db(event.source.user_id, user_message, answer)

def get_bot_name() -> str:
    bot_name = request.args['bot_name']
    return bot_name

def is_change_conversation_style_text(user_message: str) -> bool:
    return user_message in conversation_style_dict.values()

def change_conversation_style(user_message: str, user_id: str) -> str:
    for conversation_style, message in conversation_style_dict.items():
        if message == user_message:
            cleared_chat_history = []
            save_session_to_cosmos_db(user_id, conversation_style, cleared_chat_history)
            return conversation_style
    return None

def get_answer(question: str, bot_name: str, session: []) -> [str, str]:
    query = generate_query(question) if use_keyword_query else question
    search_result, top_results, file_names = search_document(query, bot_name)
    answer = generate_answer(question, search_result, session)
    if use_bing_search: answer = bing_search_if_no_answer(answer, question, session)
    add_chat_history(question, answer, session)
    return answer, top_results, file_names

def inform_change_to_line(reply_token: any, line_bot_api: any, conversation_style) -> None:
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=conversation_style_dict[conversation_style] + "しました。")
    )

def reply_answer_to_line(answer:str, top_results_str: str, reply_token: any, line_bot_api: any, session: []) -> None:
    conversation_style = session['conversation_style']
    if conversation_style == 'simple' or conversation_style == 'normal':
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=answer)
        )
    elif conversation_style == 'strict':
        answer_and_citation = "【AIによる回答】\n" + answer + "\n\n" + "【取扱説明書の抜粋】\n" + top_results_str
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=answer_and_citation)
        )

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

def generate_answer(question: str, search_result: str, session: []) -> str:
    logging.info('called generate_answer function.')
    conversation_style = session['conversation_style']
    if conversation_style == 'simple':
        style = '大雑把な'
        n_words = 30
        assistant_answer = "スイッチを引いてウォッシャー液噴射、レバーを離すとワイパー動作が停止します。リヤも同様です。操作後3秒でワイパー再作動します。"
    elif conversation_style == 'normal':
        style = '普通の'
        n_words = 50
        assistant_answer = "フロントウォッシャーを使うには、スイッチを手前に引いてウォッシャー液を噴射し、スイッチを引いている間はワイパーが作動します。\
            レバーを離すとワイパーが数回動いて停止します。"
    elif conversation_style == 'strict':
        style = '丁寧な'
        n_words = 100
        assistant_answer = "フロントウォッシャーを使うには、スイッチを手前に引いてウォッシャー液を噴射し、引いている間はワイパーも動きます。\
            レバーを離すとワイパーは数回動いて停止します。リヤウォッシャーも同様に操作でき、ウォッシャー液を噴射した後、ワイパーで拭き取ります。\
            操作後、ワイパーは約3秒後に自動的に数回動きます。"
    prompt = [
        {
            "role": "system",
            "content": f"質問と質問に回答するための情報が与えられるので、文章を{style}表現で{n_words}文字程度の1文で要約してください。\
                ただし、十分な情報が提供されていない場合は「十分な情報が提供されていないため回答できません。」と回答してください。"
        },
        {
            "role": "user",
            "content": "質問内容：ワイパー・ウォッシャーの使い方を教えて 質問に回答するための情報：ウォッシャーの使いかた■フロントウォッシャー\
                ●スイッチを手前に引くと、ウォッシャー液が噴射します。●スイッチを引いている間はウォッシャー液の噴射とワイパーの作動が続き、レバーを離すとワイパーが数回作動してから停止します\
                運転のしかたランプをつける、ワイパーを使うウォッシャーの使いかた知識フロントウォッシャー●スイッチを手前に引くと、ウォッシャー液が噴射します。\
                ●スイッチを引いている間はウォッシャー液の噴射とワイパーの作動が続き、レバーを離すとワイパーが数回作動してから停止します。リヤウォッシャー\
                ●スイッチを車両前方に押すと、ウォッシャー液が噴射します●スイッチを押している間はウォッシャー液の噴射とワイパーの作動が続き、レバーを離すとワイパーが数回作動してから停止します。\
                ●ウォッシャースイッチを操作したあと、ガラスに残ったウォッシャー液をふき取るため、約3秒後に一度ワイパーが作動します"
        },
        {
            "role": "assistant",
            "content": assistant_answer
        }
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
        max_tokens=2000,
        temperature=0.0,
    )
    answer = response['choices'][0]['message']['content']
    return answer

def search_document(query: str, bot_name: str) -> [str, [str], [str]]:
    cognitive_search_url = os.getenv('AZURE_COGNITIVE_SEARCH_ENDPOINT')
    cognitive_search_url = remove_trailing_slash(cognitive_search_url)
    index_name = bot_name + os.getenv('INDEX_NAME')
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
    return "(p. " + file_name.split('_')[1] + "に記載)"

def add_chat_history(question: str, answer: str, session: []) -> None:
    chat_history = session['chat_history']
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})
    save_session_to_cosmos_db(session['id'], session['conversation_style'], chat_history)

def get_container_client() -> any:
    connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING', None)
    cosmos_db_name = os.getenv('COSMOS_DB_NAME', None)
    cosmos_container_name = os.getenv('COSMOS_DB_CONTAINER_NAME', None)
    client = CosmosClient.from_connection_string(connection_string)
    database_client = client.get_database_client(cosmos_db_name)
    container_client = database_client.get_container_client(cosmos_container_name)
    return container_client

def insert_cosmos_db(user_id: str, input_txt: str, output_txt: str) -> None:
    try:
        container_client = get_container_client()
        dt_now_jst_aware = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        container_client.upsert_item({
                'id': str(uuid.uuid4()),
                'usage': 'log',
                'user_id': user_id,
                'question': str(input_txt),
                'answer': str(output_txt),
                'created_at': str(dt_now_jst_aware),
        })
        logging.info('Project details are stored to Cosmos DB.')
    except Exception as e:
        logging.error(e)

def save_session_to_cosmos_db(user_id: str, conversation_style: str, chat_history: []) -> None:
    try:
        container_client = get_container_client()
        dt_now_jst_aware = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        container_client.upsert_item({
                'id': user_id,
                'usage': 'session',
                'conversation_style': conversation_style,
                'chat_history': chat_history,
                'last_modified': str(dt_now_jst_aware),
        })
        logging.info('Project details are stored to Cosmos DB.')
    except Exception as e:
        logging.error(e)

def read_session_from_cosmos_db(user_id: str) -> []:
    try:
        container_client = get_container_client()
        session = container_client.read_item(item=user_id, partition_key='session')
        return session
    except Exception as e:
        logging.error(e)

def bing_search_if_no_answer(answer: str, question: str, session: []) -> str:
    if "回答できません" in answer:
        bing_results = get_bing_results(question)
        search_urls = get_urls(bing_results, count = 3)
        return answer + "\n代わりにこちらの記事を参考にしてください。\n" + search_urls[0]
    else:
        return answer

def get_bing_results(search_term: str) -> json:
    headers = {"Ocp-Apim-Subscription-Key": bing_api_subscription_key}
    params = {"q": search_term}
    response = requests.get(bing_url, headers=headers, params=params)
    response.raise_for_status()
    bing_results = response.json()
    return bing_results

def get_urls(bing_results: json, count: int) -> [str]:
    urls = []
    for result in bing_results["webPages"]["value"]:
        urls.append(result["url"])
    return urls[:count]

def get_web_text(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        main_content = soup.find('body')
        if main_content:
            raw_text = main_content.get_text()
            cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()
            return cleaned_text
        else:
            return "not found main content"
    else:
        print(f"error: status code {response.status_code}")

def get_web_texts(urls: [str]) -> [str]:
    web_texts = []
    for url in urls:
        web_texts.append(get_web_text(url))
    return web_texts

# Test Function
# Attention: Need to provide question as a parameter
# for example, <URL>?question=車両が故障したときはどうすればいいですか？&bot_name=hoge
@app.route("/test_get_answer")
def test_get_answer():
    question = get_question()
    query = generate_query(question)
    bot_name = get_bot_name()
    search_result, _, _ = search_document(query, bot_name)
    session = {'conversation_style': 'normal', 'chat_history': []}
    answer = generate_answer(question, search_result, session)
    if use_bing_search: answer = bing_search_if_no_answer(answer, question, session)
    # add_chat_history(question, answer, session)
    return answer

def get_question() -> str:
    question=request.args['question']
    return question

@app.route("/test_insert_cosmos_db")
def test_insert_cosmos_db():
    user_id = "test_user_id"
    input_txt = "test_input_txt"
    output_txt = "test_output_txt"
    insert_cosmos_db(user_id, input_txt, output_txt)
    return "inserted"

@app.route("/test_save_session_to_cosmos_db")
def test_save_session_to_cosmos_db():
    user_id = "test_user_id"
    conversation_style = "test_conversation_style"
    chat_history = ["test_chat_history"]
    save_session_to_cosmos_db(user_id, conversation_style, chat_history)
    return "saved"

@app.route("/test_read_cosmos_db")
def test_read_cosmos_db():
    user_id = "test_user_id"
    read_session_from_cosmos_db(user_id)
    return "read"

if __name__ == '__main__':
   app.run(port=80)
