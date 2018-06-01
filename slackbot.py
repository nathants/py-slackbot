import json
from urllib import parse

slash_handlers = []
event_handlers = []

def slash(command):
    def fn(f):
        slash_handlers.append([command, f])
        return f
    return fn

def event(conditional):
    def fn(f):
        event_handlers.append([conditional, f])
        return f
    return fn

def resp(body):
    return {'statusCode': '200',
            'isBase64Encoded': False,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(body) if not isinstance(body, str) else body}

def main(event, context):
    if 'body' not in event:
        return
    try:
        body = json.loads(event['body'])
    except:
        body = parse.parse_qs(event['body'])
        if 'command' in body:
            for command, handler in slash_handlers:
                if body['command'][0] == command:
                    return handler(body)
    else:
        if "challenge" in body: # event subscriptions api auth
            return resp({'challenge': body['challenge']})
        elif body['type'] == 'event_callback':
            for conditional, handler in event_handlers:
                if conditional(body['event']):
                    handler(body['event'])
                    return resp('')