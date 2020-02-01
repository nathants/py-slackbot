#!/usr/bin/env python3.6
#
# require: git+https://github.com/nathants/slackbot
# require: requests
# policy: CloudWatchLogsFullAccess
# allow: lambda:InvokeFunction *
# trigger: api
# trigger: cloudwatch rate(15 minutes) # keep lambda warm for fast responses
#

import time
import json
import requests
import slackbot
import os

slackbot.token = 'SKIP' # this should be the verification token from your slack app

def post(text):
    """
    https://api.slack.com/incoming-webhooks
    """
    requests.post(os.environ['web_hook_url'], data=json.dumps({'text': text}))

@slackbot.slash('/test', lambda text: 'stuff' in text)
def _(text):
    """
    https://api.slack.com/slash-commands
    """
    post(f'i can post to the channel. thanks for: {text}')
    return slackbot.response(f'i can also respond directly. thanks for: {text}')

@slackbot.slash_async('/test', lambda text: 'slow stuff' in text)
def _(text):
    """
    the slash command handler must return in less than 3 seconds, so
    if you need more time than that to do something, you must go async.
    """
    time.sleep(4)
    return slackbot.response(f'thanks for: {text}')

@slackbot.event(lambda event: 'foo bar' in event['text'])
def _(event):
    """
    https://api.slack.com/events-api
    """
    time = event["event_ts"]
    post(f'baz qux! from event at time: {time}')

def main(event, context):
    return slackbot.main(event, context)
