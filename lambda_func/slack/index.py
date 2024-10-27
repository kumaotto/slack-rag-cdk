import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from slack import response_within_3sec
from slack import handle_app_mention_events

# Slackアプリの初期化
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)

# Slackのメンションに対するイベントハンドラを設定
app.event("app_mention")(ack=response_within_3sec, lazy=[handle_app_mention_events])


# Lambda関数のエントリーポイント
def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
