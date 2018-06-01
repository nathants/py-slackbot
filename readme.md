# simple slackbots with python and lambda

- install [cli-aws](https://github.com/nathants/cli-aws#installation)

- go create a [slack app](https://api.slack.com/apps)

- create a slack [web hook](https://api.slack.com/incoming-webhooks) for the channel you want to post in
  - save the web hook url for later

- copy the example somewhere
  - `cp example.py ~/my_slackbot.py`

- deploy it to a [lambda](https://aws.amazon.com/lambda/) behind an [api gateway](https://aws.amazon.com/lambda/)
  - `aws-lambda-deploy --yes ~/my_slackbot.py web_hook_url="https://hooks.slack.com/services/..."`
  - save the api url for later: `aws-lambda-api ~/my_slackbot.py`

- create a slack [event subscription](https://api.slack.com/events-api)
  - enter the api url from your deployed lambda, it should verify
  - subscribe to `messages.groups` and `messages.channels`

- create a slack [slash command](https://api.slack.com/slash-commands)
  - the command should be `/test`
  - enter the api url from your deployed lambda

- go and try your slack bot!
  - typing `foo bar` into slack and hitting enter should get a response like: `baz qux!`
  - typing `/test stuff` into slack and hitting enter should get a response like: `thanks for: stuff`

- modify your slackbot
  - add more slash commands
  - respond to more messages
  - add more web hooks to other channels
  - read more about slacks [web hooks](https://api.slack.com/incoming-webhooks), [event subscriptions](https://api.slack.com/events-api), and [slash commands](https://api.slack.com/slash-commands)

- debug your lambda by tailing the logs
  - `aws-lambda-logs -f ~/my_slackbot.py`

- tear down your lambda, api, and all associated resources with
  - `aws-lambda-rm --everything ~/my_slackbot.py`
