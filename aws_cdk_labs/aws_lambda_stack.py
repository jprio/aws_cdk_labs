from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2, aws_dynamodb as dynamodb,    aws_lambda as lambda_,
    aws_events_targets as targets,    aws_events as events,
    aws_iam as iam,
    App, Stack, Duration
)
import os.path


class LambdaCronStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        with open("aws_cdk_labs/lambda-handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        role = iam.Role(self, "MyRole",
                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
                        )

        role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=["dynamodb:PutItem"]
        ))

        lambdaFn = lambda_.Function(
            self, "lmbd",
            code=lambda_.InlineCode(handler_code),
            handler="index.main",
            timeout=Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
            role=role
        )

        # Run every day at 6PM UTC
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='0',
                hour='18',
                month='*',
                week_day='MON-FRI',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))
