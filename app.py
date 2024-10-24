#!/usr/bin/env python3
import os

import aws_cdk as cdk

from slack_rag_cdk.slack_rag_cdk_stack import SlackRagCdkStack


app = cdk.App()
SlackRagCdkStack(app, "SlackRagCdkStack")

app.synth()
