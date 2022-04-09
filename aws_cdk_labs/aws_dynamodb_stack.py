from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2, aws_dynamodb as dynamodb,    aws_lambda as lambda_,
    aws_events_targets as targets,    aws_events as events,
    aws_iam as iam,
    App, Stack, Duration
)
import os.path


dirname = os.path.dirname(__file__)


class DynamoDBStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # create dynamo table
        demo_table = dynamodb.Table(
            self, "demo_table",  table_name='my-table',
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
