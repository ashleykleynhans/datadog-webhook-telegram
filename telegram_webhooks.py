import os
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
telegram_bot_chat_id = os.environ['TELEGRAM_BOT_CHAT_ID']

@app.route('/')
def ping():
    return jsonify({"status": "ok"})

@app.route('/', methods =  ['POST'])
@basic_auth.required
def webhookHandler():
    content = request.get_json()
    alert_title = content['alert_title']
    alert_query = content['alert_query']
    event_title = content['event_title']
    alert_type = content['alert_type']
    priority = content['priority']
    link = content['link']
    image = content['snapshot']
    tags = content['tags']

    url = 'https://api.telegram.org/bot' + telegram_bot_token + '/sendMessage'
    reply_markup = {'inline_keyboard': [[{'text' : '*Check Event:*','url' : link}]]}
    payload = {
        'chat_id': telegram_bot_chat_id,
        'text': '<b>Event Title:</b>\n' + event_title + '\n<b>Graph:</b>'+ image +'\n<b>Priority:</b>' + priority + '\n<b>Type:</b>'+ alert_type + '\n<b>Tags:</b>' + tags,
        'reply_markup' : json.dumps(reply_markup),
        'parse_mode' : 'html'
    }
    req = requests.post(url = url, data = payload)
    telegram_response = req.json()
    return jsonify(telegram_response)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram Datadog Webhook Receiver')
    parser.add_argument('-p','--port',help='listening port',type=int, default=8090)
    parser.add_argument('-H','--host',help='listening host',default='0.0.0.0')
    results = parser.parse_args()
    app.run(host=results.host, port=results.port)