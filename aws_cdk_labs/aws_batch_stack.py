from aws_cdk import (
                     aws_ec2 as ec2, 
                     aws_batch_alpha as batch,
                     aws_ecs as ecs,
                     App, Stack, CfnOutput
                     )
from constructs import Construct
"""
Batch achieves this by utilizing queue processing of batch job requests. To successfully submit a job for execution, you need the following resources:

* Job Definition - Group various job properties (container image, resource requirements, env variables…) into a single definition. These definitions are used at job submission time.
* Compute Environment - the execution runtime of submitted batch jobs
* Job Queue - the queue where batch jobs can be submitted to via AWS SDK/CLI

https://github.com/aws-samples/aws-cdk-examples/tree/master/python/batch


"""

class BatchStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        """
        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(
                          name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                            )
        """
        vpc = ec2.Vpc(self, "VPC")

        # To create number of Batch Compute Environment
        count = 3

        batch_ce = []

        # For loop to create Batch Compute Environments
        for i in range(count):
            name = "MyBatchEC2Env" + str(i)
            batch_environment = batch.ComputeEnvironment(self, name,
            compute_resources=batch.ComputeResources(
                type=batch.ComputeResourceType.SPOT,
                bid_percentage=75,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
                vpc=vpc
                )
            )

            batch_ce.append(batch.JobQueueComputeEnvironment(compute_environment=batch_environment,order=i))

        # Create AWS Batch Job Queue and associate all Batch CE.
        self.batch_queue = batch.JobQueue(self, "JobQueue",
                                        compute_environments=batch_ce)


        # Create Job Definition to submit job in batch job queue. 
        batch_jobDef = batch.JobDefinition(self, "MyJobDef",
                                        job_definition_name="BatchCDKJobDef",
                                        container=batch.JobDefinitionContainer(image=ecs.ContainerImage.from_registry(
                                            "public.ecr.aws/amazonlinux/amazonlinux:latest"), command=["sleep", "60"], memory_limit_mib=512, vcpus=1),
                                        )


        # Output resources
        CfnOutput(self, "BatchJobQueue",value=self.batch_queue.job_queue_name)
        CfnOutput(self, "JobDefinition",value=batch_jobDef.job_definition_name)