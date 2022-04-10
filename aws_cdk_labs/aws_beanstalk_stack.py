import boto3
import os
from constructs import Construct

from aws_cdk import (
    aws_s3_assets,     aws_iam as iam,
    aws_elasticbeanstalk as elastic_beanstalk,
    App, Stack, Duration, NestedStack, CfnOutput
)


class BeanstalkEnvStack(Stack):

    def createEnvironment(self, application_name, environment_name, solution_stack_name):

        role = iam.Role(self, "ebs-aws-elasticbeanstalk-ec2-role",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "AWSElasticBeanstalkWebTier"))
        profile_name = "ebs-aws-elasticbeanstalk-ec2-profile"

        instance_profile = iam.CfnInstanceProfile(self, profile_name,
                                                  instance_profile_name=profile_name,
                                                  roles=[role.role_name])
        # get the latest beanstalk application version
        client = boto3.client('elasticbeanstalk')

        application_versions = client.describe_application_versions(
            ApplicationName=application_name
        )

        version_label = None

        if(len(application_versions['ApplicationVersions']) > 0):
            version_label = application_versions['ApplicationVersions'][0]['VersionLabel']

        beanstalk_env_config_template = elastic_beanstalk.CfnConfigurationTemplate(
            self,
            "Elastic-Beanstalk-Env-Config",
            application_name=application_name,
            solution_stack_name=solution_stack_name,
            option_settings=[
                elastic_beanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration", option_name="IamInstanceProfile", value=profile_name
                ),

                elastic_beanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MinSize", value="2"
                ),

                elastic_beanstalk.CfnConfigurationTemplate.ConfigurationOptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MaxSize", value="4"
                )
            ]

        )
        # configure the environment for auto-scaling
        beanstalk_env = elastic_beanstalk.CfnEnvironment(
            self,
            "Elastic-Beanstalk-Environment",
            application_name=application_name,
            environment_name=environment_name,
            solution_stack_name=solution_stack_name,
            version_label=version_label,

            option_settings=[
                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration", option_name="IamInstanceProfile", value=profile_name
                ),

                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MinSize", value="2"
                ),
                elastic_beanstalk.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:asg", option_name="MaxSize", value="4"
                ),
            ]
        )

        self.beanstalk_env_config_template = beanstalk_env_config_template
        self.beanstalk_env = beanstalk_env

    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.createEnvironment(
            props['application_name'], props['environment_name'], props['solution_stack_name'])


class BeanstalkS3Stack(Stack):
    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # the asset is uploaded to the cdktoolkit-stagingbucket
        s3_bucket_asset = aws_s3_assets.Asset(
            self,
            "s3-asset",
            path=os.path.abspath(props['s3_asset'])
        )

        # debugging print s3 object url to console output
        output = CfnOutput(
            self,
            "S3_object_url",
            value=s3_bucket_asset.s3_object_url,
            description="S3 object url"
        )

        output = CfnOutput(
            self,
            "S3_object_key",
            value=s3_bucket_asset.s3_object_key,
            description="S3 object key"
        )

        output = CfnOutput(
            self,
            "S3_bucket_name",
            value=s3_bucket_asset.s3_bucket_name,
            description="S3 bucket name"
        )

        self.output_props = props.copy()
        self.output_props['s3bucket_name'] = s3_bucket_asset.s3_bucket_name
        self.output_props['s3bucket_obj_key'] = s3_bucket_asset.s3_object_key

    # pass objects to another stack

    @ property
    def outputs(self):
        return self.output_props


class BeanstalkAppStack(Stack):

    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        def createApplication(application_name):
            elastic_beanstalk.CfnApplication(
                self,
                "Elastic-Beanstalk",
                application_name=application_name,
                description="AWS Elastic Beanstalk Demo",
            )

        createApplication(props['application_name'])

        # BeanstalkAppVersionStack(
        #    self, "BeanstalkAppVersionStack", props, **kwargs)


class BeanstalkAppVersionStack(NestedStack):
    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        app_version = elastic_beanstalk.CfnApplicationVersion(
            self,
            "application_version",
            application_name=props['application_name'],
            # source_bundle=elastic_beanstalk.CfnApplicationVersion.SourceBundleProperty(
            #    s3_bucket=props['s3bucket_name'],
            #    s3_key=props['s3bucket_obj_key']
            # ),

        )
