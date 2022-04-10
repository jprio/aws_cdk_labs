#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_labs.aws_dynamodb_stack import DynamoDBStack
from aws_cdk_labs.aws_ec2_stack import EC2InstanceStack
from aws_cdk_labs.aws_lambda_stack import LambdaCronStack
from aws_cdk_labs.aws_beanstalk_stack import BeanstalkS3Stack
from aws_cdk_labs.aws_beanstalk_stack import BeanstalkAppStack
from aws_cdk_labs.aws_beanstalk_stack import BeanstalkEnvStack

app = cdk.App()
# EC2InstanceStack(app, "EC2InstanceStack",
# If you don't specify 'env', this stack will be environment-agnostic.
# Account/Region-dependent features and context lookups will not work,
# but a single synthesized template can be deployed anywhere.

# Uncomment the next line to specialize this stack for the AWS Account
# and Region that are implied by the current CLI configuration.

#env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

# Uncomment the next line if you know exactly what Account and Region you
# want to deploy the stack to. */

#env=cdk.Environment(account='123456789012', region='us-east-1'),

# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
#                 )
#DynamoDBStack(app, "DynamoDBStack")
#LambdaCronStack(app, "LambdaCronStack")


def create_ebs_stack():

    # a dictionary to store properties
    props = {
        'namespace': 'ElasticBeanstalk',
        'application_name': 'ElasticBeanstalk-app',
        'environment_name': 'ElasticBeanstalk-env',
        'solution_stack_name': '64bit Amazon Linux 2 v3.3.12 running Python 3.8',
    }

    beanstalk_app = BeanstalkAppStack(
        app,
        f"{props['namespace']}-app",
        props
    )

    # the beanstalk app stack has a dependency on the creation of a S3 bucket
    # beanstalk_app.add_dependency(s3_bucket)

    beanstalk_env = BeanstalkEnvStack(
        app,
        f"{props['namespace']}-env",
        props,

    )

    # the beanstalk environment stack has a dependency on the creation of a beanstalk app
    beanstalk_env.add_dependency(beanstalk_app)


create_ebs_stack()
app.synth()
