# Prerequisites
- Install [ngrok](https://ngrok.com/)

- Create Telegram Bot and export the Bot Token and Chat ID ( Ref: [Create New Telegram Bot](https://core.telegram.org/bots#creating-a-new-bot)

`export TELEGRAM_BOT_TOKEN='<BOT_TOKEN>'`

`export TELEGRAM_BOT_CHAT_ID='<BOT_CHAT_ID>'`

- Create new telegram channel and add the bot into it

# Datadog Webhook Configuration
- Login to Datadog
- Navigate to *Integrations* -> *Integrations* -> Search for *Webhooks* -> *Configure*

- Navigate to bottom and insert the **Name** and **URL** of the receiver

ex:
```
Name = Datadog Test
URL = https://0f379388.ngrok.io
```

- Tick `Use Custom Payload` checkbox and fill the *Custom Payload* form with below payload sample

```
{
    "event_title": "$EVENT_TITLE",
    "alert_title": "$ALERT_TITLE",
    "tags": "$TAGS",
    "user": "$USER",
    "priority": "$PRIORITY",
    "text_only_msg": "$TEXT_ONLY_MSG",
    "snapshot": "$SNAPSHOT",
    "link": "$LINK",
    "alert_query": "$ALERT_QUERY"
}
```
- Click `Save Configuration` Button

# How to Test
- Run webhook receiver -> ` python scripts/datadog_webhooks/telegram_webhooks.py`

- Create Testing Public URL using ngrok 
 -> `ngrok http 8090`

- Update datadog webhook configuration with Ngrok URL **( use https one)**

- Login to Datadog and configure Monitor to send alert to Webhook

- Check telegram channel with bot

# Deploy to Lambda

- Switch to python3.7 -> `virtualenv -p /usr/bin/python3.7 py37 && source py37/bin/activate`
- Install dependencies -> `pip3.7 install -r requirements.txt`
- Create `zappa_settings.json` and insert below lines for lambda deployment configuration

```
{
    "production": {
        "app_function": "telegram_webhooks.app",
        "aws_region": "ap-southeast-1",
        "profile_name": "dev@midas",
        "project_name": "datadog-webhook",
        "runtime": "python3.7",
        "s3_bucket": "datadog-telegram-webhooks",
        "environment_variables": {
            "TELEGRAM_BOT_TOKEN":"<BOT_TOKEN>",
            "TELEGRAM_BOT_CHAT_ID":"<BOT_CHAT_ID>"
        }
    }
}
```
- Deploy to Lambda using `zappa deploy`
- Check the API Gateway URL using `zappa status`

# Todos

- Implement HTTP Basic Authentication
- Create conditional rule for automatic failover ( ex: ldc dynamodb)





