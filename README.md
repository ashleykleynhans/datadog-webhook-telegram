# Datadog Webhook to Trigger Telegram Notifications

[![Python Version: 3.9](
https://img.shields.io/badge/Python%20application-v3.9-blue
)](https://www.python.org/downloads/release/python-3913/)
[![License: Apache 2.0](
https://img.shields.io/github/license/ashleykleynhans/datadog-webhook-telegram
)](https://opensource.org/licenses/Apache-2.0)

## Background

This project is forked from
[https://github.com/traveloka/datadog-webhook-telegram](https://github.com/traveloka/datadog-webhook-telegram).

The following changes have been made from the original:

1. Split **warnings** and **errors** into two different Telegram channels
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
5. Added a Python script to generate the Basic Authorization JSON header
that Datadog needs to use to authenticate the requests it makes to the
Webhook.
6. Upgraded docs from Python 3.7 to Python 3.9, since all Python3 versions
prior to 3.9.1 are vulnerable to
[CVE-2021-3177](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-3177).

<img src="https://raw.githubusercontent.com/ashleykleynhans/datadog-webhook-telegram/master/example.png" alt="Example Alert" width="500">

## Prerequisites

1. Install [ngrok](https://ngrok.com/).
```bash
brew install ngrok
```
2. Ensure your System Python3 version is 3.9, but greater than 3.9.1.
```bash
python3 -V
```
3. If your System Python is not 3.9:
```bash
brew install python@3.9
brew link python@3.9
```
4. If your Sytem Python is 3.9 but not greater than 3.9.1:
```bash
brew update
brew upgrade python@3.9
```
5. [Create a new Telegram Bot](https://core.telegram.org/bots#creating-a-new-bot)
and take note of the Bot Token.
6. Create two new Telegram channels, one for **warnings** and one for
**errors** and add the bot into them as an Admin user.
7. Export the environment variables that are required by the webhook:
```bash
export TELEGRAM_BOT_TOKEN='<BOT_TOKEN>'
export TELEGRAM_WARNING_CHAT_ID='<WARNING_CHAT_ID>'
export TELEGRAM_CRITICAL_CHAT_ID='<CRITICAL_CHAT_ID>'
export HTTP_AUTH_USERNAME='<USERNAME_TO_AUTH_DATADOG_WEBHOOK>'
export HTTP_AUTH_PASSWORD='<PASSWORD_TO_AUTH_DATADOG_WEBHOOK>'
```

## Datadog Webhook Configuration

1. Login to Datadog.
2. Navigate to *Integrations* -> *Integrations* -> Search for *Webhooks* -> *Configure*.
3. Navigate to the bottom and insert the **Name** and **URL** of the receiver.

eg:
<pre>
Name : Telegram_Notifications
URL : https://0f379388.ngrok.io
</pre>
4. Tick the `Use Custom Payload` checkbox and enter the following JSON content
into `Payload` input box:
```json
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
5. Tick the `Custom Headers` checkbox.
6. Ensure that the `Encode as form` checkbox is **NOT** ticked.
7. Ensure that your `HTTP_AUTH_USERNAME` and `HTTP_AUTH_PASSWORD`
environment variables are configured (see [Prerequisites](#Prerequisites) above).
8. Run the `generate_basic_auth.py` script in your terminal to generate
your Basic Authorization header for the Datadog webhook to prevent random
unauthenticated requests from being processed by your webhook.
```bash
python3 generate_basic_auth.py
```
8. This should return an HTTP Basic Authorization header in JSON format
that will be used to authenticate requests to your Webhook receiver,
for example:
```json
{
    "Authorization": "Basic d0gcatM0us3Ra8b1T"
}
```
9. Paste the JSON returned by the script into the input box below the
`Custom Headers` checkbox.
10. Click the `Save` Button.

## Testing your Webhook

1. Run the webhook receiver from your terminal.
```bash
python3 telegram_webhooks.py
```
2. Open a new terminal window and use [ngrok](https://ngrok.com/) to create
a URL that is publically accessible through the internet by creating a tunnel
to the webhook receiver that is running on your local machine.
```bash
ngrok http 8090
```
4. Note that the ngrok URL will change if you stop ngrok and run it again,
   so keep it running in a separate terminal window, otherwise you will not
   be able to test your webhook successfully.
5. Update your Datadog webhook configuration to the URL that is displayed
while ngrok is running **(be sure to use the https one)**.
6. Login to Datadog and configure a Monitor to send alerts to your Webhook
by adding the Webhook name in the `Notify your team` section,
eg. `@webhook-Telegram_Notifications`.  You will probably want to either
clone an existing Monitor and lower the thresholds dramatically so
that alerts can be triggered for testing purposes, or alternatively create
a new Monitor also setting the thresholds to values that will trigger
notifications that will allow you to test your Webhook.
7. Check your Telegram channels that you crated for your Datadog notifications
that have the bot running within them.

## Deploy to AWS Lambda

1. Create a Python 3.9 Virtual Environment:
```bash
python3 -m venv venv/py3.9
source venv/py3.9/bin/activate
```
2. Upgrade pip.
```bash
python3 -m pip install --upgrade pip
```
3. Install the Python dependencies that are required by the Webhook receiver:
```bash
pip3 install -r requirements.txt
```
4. Create a file called `zappa_settings.json` and insert the JSON content below
to configure your AWS Lambda deployment:
```json
{
    "production": {
        "app_function": "telegram_webhooks.app",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "datadog-webhook",
        "runtime": "python3.9",
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
5. Use [Zappa](https://github.com/Zappa/Zappa) to deploy your Webhook
to AWS Lambda (this is installed as part of the dependencies above):
```bash
zappa deploy
```
6. Take note of the URL that is returned by the `zappa deploy` command,
eg. `https://1d602d00.execute-api.us-east-1.amazonaws.com/production`
   (obviously use your own and don't copy and paate this one, or your
Webhook will not work).

**NOTE:** If you get the following error when running the `zappa deploy` command:

<pre>
botocore.exceptions.ClientError:
An error occurred (IllegalLocationConstraintException) when calling
the CreateBucket operation: The unspecified location constraint
is incompatible for the region specific endpoint this request was sent to.
</pre>

This error usually means that your S3 bucket name is not unique, and that you
should change it to something different, since the S3 bucket names are not
namespaced and are global for everyone.

7. Check the status of the API Gateway URL that was created by zappa:
```bash
zappa status
```
8. Test your webhook by making a curl request to the URL that was returned
by `zappa deploy`:
```
curl https://1d602d00.execute-api.us-east-1.amazonaws.com/production
```
You should expect the following response:
```json
{"status":"ok"}
```
9. Update your Webhook URL in Datadog to the one returned by the
`zappa deploy` command.
