#!/usr/bin/env python3
import os
import io
import html
import argparse
import json
import requests
import time
from flask import Flask, request, jsonify, make_response
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = os.environ['HTTP_AUTH_USERNAME']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['HTTP_AUTH_PASSWORD']
basic_auth = BasicAuth(app)
telegram_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
telegram_warning_chat_id = os.environ['TELEGRAM_WARNING_CHAT_ID']
telegram_critical_chat_id = os.environ['TELEGRAM_CRITICAL_CHAT_ID']


def get_args():
    parser = argparse.ArgumentParser(
        description='Telegram Datadog Webhook Receiver'
    )

    parser.add_argument(
        '-p', '--port',
        help='Port to listen on',
        type=int,
        default=8090
    )

    parser.add_argument(
        '-H', '--host',
        help='Host to bind to',
        default='0.0.0.0'
    )

    return parser.parse_args()


def send_telegram_notification(datadog_payload):
    alert_priority = datadog_payload['alert_priority']
    alert_query = datadog_payload['alert_query']
    alert_status = datadog_payload['alert_status']
    alert_title = datadog_payload['alert_title']
    alert_transition = datadog_payload['alert_transition']
    alert_type = datadog_payload['alert_type']
    event_title = datadog_payload['event_title']
    event_type= datadog_payload['event_type']
    link = datadog_payload['link']
    priority = datadog_payload['priority']
    snapshot = datadog_payload['snapshot']
    text_only_msg = datadog_payload['text_only_msg']
    tags = datadog_payload['tags']
    user = datadog_payload['user']

    if alert_type == 'error':
        chat_id = telegram_critical_chat_id
    else:
        chat_id = telegram_warning_chat_id

    msg_txt = f'<b>{html.escape(event_title)}</b>\n\n'
    msg_txt += f'{html.escape(alert_status)}'

    reply_markup = {
        'inline_keyboard': [
            [
                {
                    'text': 'Check Event',
                    'url': link
                }
            ]
        ]
    }

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
        # Sleep for 5 seconds before downloading the image, to give DataDog
        # time to render it, otherwise we download an empty image.
        time.sleep(5)
        remote_image = requests.get(snapshot)
        photo = io.BytesIO(remote_image.content)
        photo.name = 'img.png'
        files = {'photo': photo}

    bot_url = f'https://api.telegram.org/bot{telegram_bot_token}/{bot_endpoint}'
    req = requests.post(url=bot_url, data=msg_data, files=files)
    return req.json()



@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(
        {
            'status': 'error',
            'msg': f'{request.url} not found',
            'detail': str(error)
        }
    ), 404)


@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify(
        {
            'status': 'error',
            'msg': 'Internal Server Error',
            'detail': str(error)
        }
    ), 500)


@app.route('/')
def ping():
    return make_response(jsonify(
        {
            'status': 'ok'
        }
    ), 200)


@app.route('/', methods=['POST'])
@basic_auth.required
def webhook_andler():
    datadog_payload = request.get_json()
    telegram_response = send_telegram_notification(datadog_payload)

    if not telegram_response['ok']:
        return make_response(jsonify(
            {
                'status': 'error',
                'msg': f'Failed to send Telegram notification to chat id: {telegram_chat_id}',
                'detail': telegram_response
            }
        ), 500)

    return jsonify(telegram_response)


if __name__ == '__main__':
    args = get_args()
    app.run(host=args.host, port=args.port)
