import json
import requests
import os
import boto3
from urllib import parse

token = None
slash_handlers = []
event_handlers = []
delayed_handlers = []

def delayed(command):
    def fn(f):
        delayed_handlers.append([command, f])
        return f
    return fn

def slash(command, conditional=lambda text: True):
    def fn(f):
        slash_handlers.append([conditional, command, f])
        return f
    return fn

def event(conditional):
    def fn(f):
        event_handlers.append([conditional, f])
        return f
    return fn

def resp(body, public=False, response_url=None):
    if not isinstance(body, dict):
        body = {'text': body}
    if public:
        body["response_type"] = "in_channel"
    body = json.dumps(body)
    if response_url:
        resp = requests.post(response_url, data=body)
        assert str(resp.status_code)[0] == '2', [resp, resp.text]
    else:
        return {'statusCode': '200', 'isBase64Encoded': False, 'headers': {'Content-Type': 'application/json'}, 'body': body}

def delay(command, response_url, data, _file_):
    name = os.path.basename(_file_).replace(' ', '-').replace('_', '-').split('.py')[0] # copied from: cli_aws.lambda_name()
    val = {'body': json.dumps({'type': 'delayed',
                               'data': data,
                               'response_url': response_url,
                               'command': command,
                               'token': token})}
    print(boto3.client('lambda').invoke(FunctionName=name,
                                        InvocationType='Event',
                                        Payload=bytes(json.dumps(val), 'utf-8')))

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
            for conditional, command, handler in slash_handlers:
                if body['command'][0] == command and conditional(body.get("text", [''])[0]):
                    return handler(body.get("text", [''])[0], body['response_url'][0])
    else:
        if "challenge" in body:
            return resp({'challenge': body['challenge']})
        elif body['type'] == 'event_callback':
            for conditional, handler in event_handlers:
                if conditional(body['event']):
                    handler(body['event'])
                    return resp('')
        elif body['type'] == 'delayed':
            for command, handler in delayed_handlers:
                if body['command'] == command:
                    handler(body['response_url'], body['data'])
                    return resp('')
    if log_unmatched_events:
        print(f'nothing matched: {body}')
