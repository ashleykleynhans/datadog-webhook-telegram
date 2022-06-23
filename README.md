# DataDog Webhook to Trigger Telegram Notifications

This project is forked from
[https://github.com/traveloka/datadog-webhook-telegram](https://github.com/traveloka/datadog-webhook-telegram).

The following changes have been made from the original:

1. Split warnings and errors into two different Telegram channels
(`TELEGRAM_WARNING_CHAT_ID` and `TELEGRAM_CRITICAL_CHAT_ID`).
2. Use `sendPhoto` endpoint for warnings and errors, and
`sendMessage` endpoint when the alert recovers, so that the
graphs look better, and so that the message is cleaner without
the link to the graph in it.
3. Reformatted the message content to only include `event_title`
and `alert_status`, to make the messages cleaner, but added
support for some additional fields in the webhook if anyone else
wants to use them.
4. Added missing auth credentials to the documentation.

## Prerequisites

1. Install [ngrok](https://ngrok.com/).
2. Create Telegram Bot and export the Bot Token and Chat ID
(Ref: [Create New Telegram Bot](https://core.telegram.org/bots#creating-a-new-bot).
```bash
export TELEGRAM_BOT_TOKEN='<BOT_TOKEN>'
export TELEGRAM_WARNING_CHAT_ID='<WARNING_CHAT_ID>'
export TELEGRAM_CRITICAL_CHAT_ID='<CRITICAL_CHAT_ID>'
export HTTP_AUTH_USERNAME='<USERNAME_TO_AUTH_DATADOG_WEBHOOK>'
export HTTP_AUTH_PASSWORD='<PASSWORD_TO_AUTH_DATADOG_WEBHOOK>'
```
3. Create two new Telegram channels, one for warnings and one for
errors and add the bot into them.

## Datadog Webhook Configuration

1. Login to Datadog.
2. Navigate to *Integrations* -> *Integrations* -> Search for *Webhooks* -> *Configure*.
3. Navigate to bottom and insert the **Name** and **URL** of the receiver.

eg:
```bash
Name = Datadog Test
URL = https://0f379388.ngrok.io
```
4. Tick `Use Custom Payload` checkbox and fill the *Custom Payload* form with below payload sample
```
{
    "alert_priority": "$ALERT_PRIORITY",
    "alert_query": "$ALERT_QUERY",
    "alert_status": "$ALERT_STATUS",
    "alert_title": "$ALERT_TITLE",
    "alert_transition": "$ALERT_TRANSITION",
    "alert_type": "$ALERT_TYPE",
    "event_title": "$EVENT_TITLE",
    "event_type": "$EVENT_TYPE",
    "link": "$LINK",
    "priority": "$PRIORITY",
    "snapshot": "$SNAPSHOT",
    "text_only_msg": "$TEXT_ONLY_MSG",
    "tags": "$TAGS",
    "user": "$USER"
}
```
5. Click `Save Configuration` Button.

## How to Test

1. Run webhook receiver.
```bash
python3 telegram_webhooks.py
```
2. Create Testing Public URL using [ngrok](https://ngrok.com/).
```bash
ngrok http 8090
```
3. Update datadog webhook configuration with Ngrok URL **(use https one)**.
4. Login to Datadog and configure Monitor to send alert to Webhook.
5. Check the Telegram channels with bot in them.

## Deploy to Lambda

1. Switch to python3.10.
```bash
virtualenv -p /usr/bin/python3.7 py37 && source py37/bin/activate
```
2. Install dependencies.
```bash
pip3.7 install -r requirements.txt
```
3. Create `zappa_settings.json` and insert below lines for lambda deployment configuration,
```
{
    "production": {
        "app_function": "telegram_webhooks.app",
        "aws_region": "us-east-1",
        "profile_name": "dev@midas",
        "project_name": "datadog-webhook",
        "runtime": "python3.10",
        "s3_bucket": "datadog-telegram-webhooks",
        "environment_variables": {
            "TELEGRAM_BOT_TOKEN":"<BOT_TOKEN>",
            "TELEGRAM_WARNING_CHAT_ID":"<WARNING_CHAT_ID>",
            "TELEGRAM_CRITICAL_CHAT_ID":"<CRITICAL_CHAT_ID>",
            "HTTP_AUTH_USERNAME":"<HTTP_AUTH_USERNAME>",
            "HTTP_AUTH_PASSWORD":"<HTTP_AUTH_PASSWORD>"
        }
    }
}
```
4. Deploy to Lambda using
```bash
zappa deploy
```
5. Check the API Gateway URL using
```bash
zappa status
```
