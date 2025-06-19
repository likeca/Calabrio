import json
import logging
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_message(message):
    if not isinstance(message.get('messageText'), str):
        return False, 'messageText must be a string'

    text = message['messageText']
    if len(text) < 10 or len(text) > 100:
        return False, 'messageText must be 10 ~ 100 characters'

    try:
        datetime.strptime(message['messageDatetime'], '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return False, 'Invalid datetime format (YYYY-MM-DD HH:MM:SS)'

    return True, ''


def handler(event, context):
    try:
        logger.info(f'Received event: {json.dumps(event)}')
        # body = event
        body = json.loads(event.get('body', '{}'))
        required_fields = ['messageUUID', 'messageText', 'messageDatetime']
        for field in required_fields:
            if field not in body:
                logger.error(f'Missing field: {field}')
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Missing field: {field}')
                }

        is_valid, error_msg = validate_message(body)
        if not is_valid:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': error_msg})
            }

        # Save to DynamoDB
        table_name = 'MessageProcessingStack-MessagesTable05B58A27-6F1ZSIT6IIDO'
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        item = {
            'messageUUID': body['messageUUID'],
            'messageText': body['messageText'],
            'messageDatetime': body['messageDatetime']
        }

        table.put_item(Item=item)
        logger.info(f'Message stored: {body['messageUUID']}')

        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'Message processed'})
        }
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error - {e}'})
        }
