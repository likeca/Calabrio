# Calabrio
Implement a serverless solution (Python script) to process and store messages.  
This implementation should be python script with aws_cdk package only.  

Requirements:  
    - Create an AWS Lambda function (with aws_cdk, specifically DockerImageFunction):  
        - The Lambda function should accept an input event containing a message, for example:  
        {. 
            "messageUUID": "05ceddd6-67e2-429a-a9c3-ea3edf6dbc7e",  
            "messageText": "placeholder message",  
            "messageDatetime": "YYYY-MM-DD HH:MM:SS". 
        }. 
        - Validate the messageText is a string and meets basic conditions (e.g., length between 10 and 100 characters).  
        - Save the validated message to an Amazon DynamoDB table (mentioned below).  
        - An API Gateway to invoke the Lambda function.  
    - Create a DynamoDB table with necessary partition key and indexes.  

Bonus (Optional):  
    - Implement error handling and logging in the Lambda function.  
    - Use environment variables for configuration (e.g., table name).  
    - Include tests for the Lambda function using a Python testing framework like pytest.  
  
Deliverables:  
    A GitHub repository containing:  
        - CDK stack code to deploy the required resources. (ie. Lambda, DynamoDB, Role, Permission, etc). 
        - A README with clear instructions on how to deploy and test the solution.  

  
# 1. Prerequisite
[AWS CDK CLI Reference](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
```bash
# 1. Install CDK CLI

# 2. Setup AWS Profile
aws configure --profile demo
# AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name [None]: ca-cantral-1
# Default output format [None]: json
```

# 2. Deployment from CDK
```bash
cd Calabrio

cdk --profile demo bootstrap
cdk --profile demo synth

cdk --profile demo deploy
cdk --profile demo destroy
```

# 3. Get CDK outputs: APIEndpoint, TableName
## 3.1 Update DynamoDB Table Name "table_name" in lambda/app.py (Line 50) from CDK Output
```bash
# table_name = 'MessageProcessingStack-MessagesTable05B58A27-6F1ZSIT6IIDO'

# Deploy lambda function
cdk --profile demo deploy
```

## 3.2 Test API Call from Shell
```bash
# Get APIEndpoint, replace the URL below
curl --location 'https://m4knk3i60f.execute-api.ca-central-1.amazonaws.com/messages' \
--header 'Content-Type: application/json' \
--data '{
    "messageUUID": "05ceddd6-67e2-429a-a9c3-ea3edf6dbc7e",
    "messageText": "placeholder message",
    "messageDatetime": "2025-06-18 19:00:00"
}'
```

# AWS CloudWatch Log
/aws/lambda/message-processing


# Test
```bash
export AWS_CDK_STACK_NAME="MessageProcessingStack"

cd lambda
pytest ./tests/message_processing.py
```