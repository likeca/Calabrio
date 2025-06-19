import json
from aws_cdk import (
    Stack,
    aws_lambda,
    aws_dynamodb,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    CfnOutput
)
from constructs import Construct


class MessageProcessingStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # # Lambda ECR Repository
        # ecr_repository = ecr.Repository(
        #     self,
        #     "message-processing",
        #     repository_name="message-processing",
        #     image_scan_on_push=True,
        #     image_tag_mutability=ecr.TagMutability.MUTABLE
        # )
        # # ecr_image = aws_lambda.EcrImageCode.from_asset_image(
        # #     directory=os.path.join(os.getcwd(), "message-processing")
        # # )

        # # Lambda IAM Role
        # lambda_role = iam.Role(
        #     self,
        #     'MessageProcessingLambdaRole',
        #     assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
        #     description='Role for Message Processing Lambda',
        # )

        # lambda_role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "AWSLambdaBasicExecutionRolePolicy",
        #         statements=[
        #             iam.PolicyStatement(
        #                 actions=[
        #                     'logs:CreateLogGroup'
        #                 ],
        #                 effect=iam.Effect.ALLOW,
        #                 resources=[f'arn:aws:logs:ca-central-1:{self.account}:*']
        #             ),
        #             iam.PolicyStatement(
        #                 actions=[
        #                     "logs:CreateLogStream",
        #                     "logs:PutLogEvents"
        #                 ],
        #                 effect=iam.Effect.ALLOW,
        #                 # Todo: update lambda name
        #                 resources=[f'arn:aws:logs:ca-central-1:{self.account}:log-group:/aws/lambda/test:*']
        #             )
        #         ]
        #     ))

        # Lambda Function
        lambda_function = aws_lambda.DockerImageFunction(
            self,
            id="DockerImageFunction",
            description="Message Processing Lambda Container Function",
            code=aws_lambda.DockerImageCode.from_image_asset(
                directory="lambda",
                cmd=["app.handler"]
            ),
            function_name="message-processing",
            architecture=aws_lambda.Architecture.X86_64
        )

        # DynamoDB Table
        table = aws_dynamodb.Table(
            self,
            'MessagesTable',
            partition_key=aws_dynamodb.Attribute(
                name='messageUUID',
                type=aws_dynamodb.AttributeType.STRING
            ),
        )

        # Add GSI for datetime queries
        table.add_global_secondary_index(
            index_name='byDatetime',
            partition_key={
                'name': 'messageDatetime',
                'type': aws_dynamodb.AttributeType.STRING
            }
        )

        # Grant Lambda access to DynamoDB
        table.grant_write_data(lambda_function)

        # API Gateway
        api = apigw.HttpApi(
            self, 'MessageAPI',
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=['*'],
                allow_methods=[apigw.CorsHttpMethod.POST],
                allow_headers=['Content-Type']
            )
        )

        api.add_routes(
            path='/messages',
            methods=[apigw.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                'LambdaIntegration', lambda_function
            )
        )

        # Outputs
        CfnOutput(self, 'APIEndpoint', value=api.url)
        CfnOutput(self, 'TableName', value=table.table_name)

        # with open("env.json", "w", encoding="utf-8") as w_file:
        #     env = {
        #         "APIEndpoint": str(api.url),
        #         "TableName": str(table.table_name)
        #     }
        #     json.dump(env, w_file, indent=4)
