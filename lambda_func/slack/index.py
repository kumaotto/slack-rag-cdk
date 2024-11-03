import json
import boto3
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

from slack import response_within_3sec, handle_app_mention_events
from ssm_utils import SSMUtils

ssm_utils = SSMUtils()

# Slackアプリの初期化
app = App(
    token=ssm_utils.get_parameter("/slack/token"),
    signing_secret=ssm_utils.get_parameter("/slack/secret"),
    process_before_response=True,
)

app.event("app_mention")(ack=response_within_3sec, lazy=[handle_app_mention_events])

# Slackのリクエストを取得するハンドラに変更
def handler(event, context):
    
    # slackのチャレンジリクエスト用
    body = json.loads(event["body"])
    if body.get("type") == "url_verification":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"challenge": body["challenge"]}),
        }

    # リトライの場合は何もしない
    if 'X-Slack-Retry-Num' in event['headers']:
        return {
            "statusCode": 200,
            "body": json.dumps({ "message": "This is a retry request." })
        }
    
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)