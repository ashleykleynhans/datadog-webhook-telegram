import os
import io
import html
import argparse
import json
import requests
from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = os.environ['HTTP_AUTH_USERNAME']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['HTTP_AUTH_PASSWORD']
basic_auth = BasicAuth(app)
telegram_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
telegram_warning_chat_id = os.environ['TELEGRAM_WARNING_CHAT_ID']
telegram_critical_chat_id = os.environ['TELEGRAM_CRITICAL_CHAT_ID']


@app.route('/')
def ping():
    return jsonify({"status": "ok"})


@app.route('/', methods =  ['POST'])
@basic_auth.required
def webhookHandler():
    content = request.get_json()
    alert_priority = content['alert_priority']
    alert_query = content['alert_query']
    alert_status = content['alert_status']
    alert_title = content['alert_title']
    alert_transition = content['alert_transition']
    alert_type = content['alert_type']
    event_title = content['event_title']
    event_type= content['event_type']
    link = content['link']
    priority = content['priority']
    snapshot = content['snapshot']
    text_only_msg = content['text_only_msg']
    tags = content['tags']
    user = content['user']

    if alert_type == 'error':
        chat_id = telegram_critical_chat_id
    else:
        chat_id = telegram_warning_chat_id

    msg_txt = f'<b>{html.escape(event_title)}</b>\n\n'
    msg_txt += f'{html.escape(alert_status)}'

    reply_markup = {'inline_keyboard': [[{'text' : 'Check Event','url' : link}]]}

    msg_data = {
        'chat_id': chat_id,
        'reply_markup': json.dumps(reply_markup),
        'parse_mode': 'html'
    }

    if snapshot == 'null':
        bot_endpoint = 'sendMessage'
        msg_data['text'] = msg_txt
        files = {}
    else:
        bot_endpoint = 'sendPhoto'
        msg_data['caption'] = msg_txt
        remote_image = requests.get(snapshot)
        photo = io.BytesIO(remote_image.content)
        photo.name = 'img.png'
        files = {'photo': photo}

    bot_url = f'https://api.telegram.org/bot{telegram_bot_token}/{bot_endpoint}'
    req = requests.post(url=bot_url, data=msg_data, files=files)
    telegram_response = req.json()

    return jsonify(telegram_response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram Datadog Webhook Receiver')
    parser.add_argument('-p','--port',help='listening port',type=int, default=8090)
    parser.add_argument('-H','--host',help='listening host',default='0.0.0.0')
    results = parser.parse_args()
    app.run(host=results.host, port=results.port)
