from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,aws_batch as batch, Stack
)
import os.path

from aws_cdk.aws_s3_assets import Asset

dirname = os.path.dirname(__file__)
"""
Batch achieves this by utilizing queue processing of batch job requests. To successfully submit a job for execution, you need the following resources:

* Job Definition - Group various job properties (container image, resource requirements, env variables…) into a single definition. These definitions are used at job submission time.
* Compute Environment - the execution runtime of submitted batch jobs
* Job Queue - the queue where batch jobs can be submitted to via AWS SDK/CLI
"""

class BatchInstanceStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(
                          name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                      )

                # default is managed
        aws_managed_environment = batch.ComputeEnvironment(self, "AWS-Managed-Compute-Env",
            compute_resources=batch.ComputeResources(
                vpc=vpc
            )
        )

        customer_managed_environment = batch.ComputeEnvironment(self, "Customer-Managed-Compute-Env",
            managed=False
        )