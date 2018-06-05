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

@slackbot.delayed('do slow thing')
def _(response_url, data):
    # the slash command handler must return in less than 3 seconds, so if you
    # need more time than that to do something, you must delay.
    time.sleep(4)
    return slackbot.resp(f'thanks for: {data}', response_url=response_url, public=True)

def post(text):
    """
    https://api.slack.com/incoming-webhooks
    """
    requests.post(os.environ['web_hook_url'], data=json.dumps({'text': text}))

@slackbot.slash('/test', lambda x: 'stuff' in x)
def _(text, response_url):
    """
    https://api.slack.com/slash-commands
    """
    post(f'i can post to the channel. thanks for: {text}')
    slackbot.delay('do slow thing', response_url, 'i can also do work slowly and async', __file__)
    return slackbot.res(f'i can also respond directly. thanks for: {text}')

@slackbot.event(lambda x: 'foo bar' in x['text'])
def _(event):
    """
    https://api.slack.com/events-api
    """
    time = event["event_ts"]
    post(f'baz qux! from event at time: {time}')

def main(event, context):
    return slackbot.main(event, context)
