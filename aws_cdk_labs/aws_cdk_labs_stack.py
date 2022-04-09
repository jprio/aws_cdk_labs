from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2, aws_dynamodb as dynamodb,    aws_lambda as lambda_,
    aws_events_targets as targets,    aws_events as events,
    aws_iam as iam,
    App, Stack, Duration
)
import os.path

from aws_cdk.aws_s3_assets import Asset

dirname = os.path.dirname(__file__)


class EC2InstanceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(
                          name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                      )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonSSMManagedInstanceCore"))

        # Instance
        instance = ec2.Instance(self, "Instance",
                                instance_type=ec2.InstanceType("t3.nano"),
                                machine_image=amzn_linux,
                                vpc=vpc,
                                role=role
                                )

        # Script in S3 as Asset
        asset = Asset(self, "Asset", path=os.path.join(
            dirname, "configure.sh"))
        local_path = instance.user_data.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key
        )

        # Userdata executes script from S3
        instance.user_data.add_execute_file_command(
            file_path=local_path
        )
        asset.grant_read(instance.role)


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
