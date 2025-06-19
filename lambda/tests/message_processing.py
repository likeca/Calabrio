import os
import boto3
import logging
import pytest
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestApiGateway:
    @pytest.fixture()
    def api_gateway_url(self):
        stack_name = os.environ.get('AWS_CDK_STACK_NAME')

        if stack_name is None:
            raise ValueError('Please set the AWS_CDK_STACK_NAME environment variable to the name of your stack')

        session = boto3.session.Session(profile_name='demo')
        client = session.client('cloudformation')

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            logger.error(f'Cannot find stack {stack_name}. Please make sure a stack with the name {stack_name} exists. Error: {str(e)}')

        stacks = response['Stacks']
        stack_outputs = stacks[0]['Outputs']
        api_outputs = [output for output in stack_outputs if output['OutputKey'] == 'APIEndpoint']

        if not api_outputs:
            raise KeyError(f'API not found in stack {stack_name}')

        return api_outputs[0]['OutputValue']

    def test_api_gateway(self, api_gateway_url):
        print(api_gateway_url)
        response = requests.get(f'{api_gateway_url}messages')
        response = requests.post(
            f'{api_gateway_url}messages',
            json={
                "messageUUID": "05ceddd6-67e2-429a-a9c3-ea3edf6dbc7e",
                "messageText": "placeholder message",
                "messageDatetime": "2025-06-18 19:00:00"
            },
            timeout=5
        )

        assert response.status_code == 200
        assert response.json() == {"status": "Message processed"}
