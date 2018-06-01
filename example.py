#!/usr/bin/env python3.6
#
# require: git+https://github.com/nathants/slackbot
# require: requests
# policy: CloudWatchLogsFullAccess
# trigger: api
# trigger: cloudwatch rate(15 minutes) # keep lambda warm for fast responses
#

import json
import requests
import slackbot
import os

def post(text):
    """
    https://api.slack.com/incoming-webhooks
    """
    requests.post(os.environ['web_hook_url'], data=json.dumps({'text': text}))

@slackbot.slash('/test')
def _(body):
    """
    https://api.slack.com/slash-commands
    """
    text = body["text"][0]
    post(f'i can post to the channel. thanks for: {text}')
    return slackbot.resp(f'i can also respond directly. thanks for: {text}')

@slackbot.event(lambda e: 'foo bar' in e['text'])
def _(event):
    """
    https://api.slack.com/events-api
    """
    time = event["event_ts"]
    post(f'baz qux! from event at time: {time}')

def main(event, context):
    return slackbot.main(event, context)
