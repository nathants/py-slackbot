import json
import inspect
import requests
import os
import boto3
from urllib import parse

ASYNC = 'async'
token = None
slash_handlers = []
event_handlers = []

def slash(command, conditional=lambda text: True):
    def fn(f):
        slash_handlers.append([conditional, command, f, None])
        return f
    return fn

def slash_async(command, conditional=lambda text: True):
    def fn(f):
        slash_handlers.append([conditional, command, f, ASYNC])
        return f
    return fn

def event(conditional):
    def fn(f):
        event_handlers.append([conditional, f])
        return f
    return fn

def _lambda_response(body):
    return {'statusCode': '200',
            'isBase64Encoded': False,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(body)}

def response(body, in_channel=True):
    if not isinstance(body, dict):
        body = {'text': body}
    if in_channel:
        body["response_type"] = 'in_channel'
    else:
        body["response_type"] = 'ephemeral'
    return body

def asynchronous(command, response_url, data, _file_):
    name = os.path.basename(_file_).replace(' ', '-').replace('_', '-').split('.py')[0] # copied from: cli_aws.lambda_name()
    val = {'body': json.dumps({'type': ASYNC,
                               'data': data,
                               'response_url': response_url,
                               'command': command,
                               'token': token})}
    boto3.client('lambda').invoke(FunctionName=name,
                                  InvocationType='Event',
                                  Payload=bytes(json.dumps(val), 'utf-8'))

def main(event, context, log_unmatched_events=False):
    if not token:
        return print('error: must assign slackbot.token = "your verification token from the app page"')
    if token == 'SKIP':
        print('warning: you should set slackbot.token to the verification token from your slack app page')
    if 'body' not in event:
        return print(f'error: no body in event {event}')
    try:
        body = json.loads(event['body'])
        if body['token'] != token or token == 'SKIP':
            return print(f'error: token mismatch {body["token"]} {token}')
    except:
        body = parse.parse_qs(event['body'])
        if body['token'][0] != token or token == 'SKIP':
            return print(f'error: token mismatch {body["token"][0]} {token}')
        if 'command' in body:
            for conditional, command, handler, kind in slash_handlers:
                text = body.get("text", [''])[0]
                if body['command'][0] == command and conditional(text):
                    if kind == ASYNC:
                        asynchronous(command, body['response_url'][0], text, inspect.getfile(handler))
                        return _lambda_response(response('one moment please...'))
                    else:
                        return _lambda_response(handler(text))
    else:
        if "challenge" in body:
            return _lambda_response({'challenge': body['challenge']})
        elif body['type'] == 'event_callback':
            for conditional, handler in event_handlers:
                if conditional(body['event']):
                    handler(body['event'])
                    return _lambda_response('')
        elif body['type'] == ASYNC:
            for conditional, command, handler, kind in slash_handlers:
                text = body['data']
                if body['command'] == command and kind == ASYNC and conditional(text):
                    resp = requests.post(body['response_url'], data=json.dumps(handler(text)))
                    assert str(resp.status_code)[0] == '2', [resp, resp.text]
                    return _lambda_response('')
    if log_unmatched_events:
        print(f'nothing matched: {body}')
