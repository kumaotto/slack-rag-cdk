from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_lambda_python_alpha as lambda_alpha,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct


class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """
        Systems Manager
        """
        slack_token = ssm.StringParameter.value_for_string_parameter(
            self,
            "/slack/token",
        )
        slack_secret = ssm.StringParameter.value_for_string_parameter(
            self,
            "/slack/secret",
        )

        """
        Lambda
        """
        # Lambda Layer
        common_layer = lambda_alpha.PythonLayerVersion(
            self,
            "SlackCommonLayer",
            entry="lambda_func/layer",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="A layer that contains the common functions.",
        )

        slack_function = _lambda.Function(
            self, "SlackRagCdkFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_asset("./lambda_func/slack"),
            timeout=Duration.seconds(30),
            layers=[common_layer],
            environment={
                "SLACK_BOT_TOKEN": slack_token,
                "SLACK_SIGNING_SECRET": slack_secret,
            }
        )

        slack_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:*",
                    "dynamodb:*",
                    "lambda:InvokeFunction",
                    "ssm:GetParameter"
                ],
                resources=["*"],
            )
        )

        """
        API Gateway
        """
        api = apigateway.RestApi(
            self,
            "SlackApi",
            rest_api_name="slack-api",
            description="Slack RAG用のAPI",
        )

        slack_events = api.root.add_resource("slack").add_resource("events")
        slack_events.add_method("POST", apigateway.LambdaIntegration(slack_function))


        """
        DynamoDB
        """
        table = dynamodb.Table(
            self,
            "SlackRAGChatCache",
            partition_key={"name": "session_id", "type": dynamodb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY, 
        )
        
        """
        Output
        """
        CfnOutput(self, "API Gateway Url",
            value=api.url_for_path("/slack/events"),
            description="The endpoint for the API"
        )