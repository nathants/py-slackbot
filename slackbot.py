import json
from urllib import parse

token = None
slash_handlers = []
event_handlers = []

def slash(command, conditional=lambda _: True):
    def fn(f):
        slash_handlers.append([conditional, command, f])
        return f
    return fn

def event(conditional):
    def fn(f):
        event_handlers.append([conditional, f])
        return f
    return fn

def resp(body, public=False):
    if public:
        body = {"response_type": "in_channel", "text": body}
    x = {'statusCode': '200',
         'isBase64Encoded': False,
         'headers': {'Content-Type': 'application/json'},
         'body': json.dumps(body) if not isinstance(body, str) else body}
    return x

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
                    return handler(body.get("text", [''])[0])
    else:
        if "challenge" in body:
            return resp({'challenge': body['challenge']})
        elif body['type'] == 'event_callback':
            for conditional, handler in event_handlers:
                if conditional(body['event']):
                    handler(body['event'])
                    return resp('')
    if log_unmatched_events:
        print(f'nothing matched: {body}')
