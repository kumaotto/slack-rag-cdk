import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_app.cdk_app_stack import SlackRagCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in slack_rag_cdk/slack_rag_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SlackRagCdkStack(app, "slack-rag-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
