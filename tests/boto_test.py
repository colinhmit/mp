import boto3

# Create the Boto3 Session
session = boto3.Session(
    aws_access_key_id='AKIAJJYQ67ESV5S4YVHQ',
    aws_secret_access_key='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',
    region_name='us-west-2',
)

client = session.client('sqs')
 
# Get the Queue URL
response = client.get_queue_url(QueueName='mpq')
url = response['QueueUrl']


messages = client.receive_message(
QueueUrl=url,
AttributeNames=['All'],
MaxNumberOfMessages=1,
VisibilityTimeout=60,
WaitTimeSeconds=5
)


if messages.get('Messages'):
    m = messages.get('Messages')[0]
    print m
    body = m['Body']
    receipt_handle = m['ReceiptHandle']
    print body
    response = client.delete_message(
                    QueueUrl=url,
                    ReceiptHandle=receipt_handle
                )