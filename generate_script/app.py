import json
import boto3
import os
import cfnresponse

def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    # Script Template for Conversion Glue Job
    script_template = ""

    # Read Script Template
    script_template_file = os.environ['LAMBDA_TASK_ROOT'] + '/glueJobScript.template'
    with open(script_template_file, 'r') as template_file:
        script_template=template_file.read()

    # Replace Placeholder Values with ResourceProperties
    script_template = script_template.replace('[S_ITEM_ID]', event['ResourceProperties']['SourceColumnItemId'])
    script_template = script_template.replace('[D_ITEM_ID]', event['ResourceProperties']['DestinationColumnItemId'])
    script_template = script_template.replace('[S_USER_ID]', event['ResourceProperties']['SourceColumnUserId'])
    script_template = script_template.replace('[D_USER_ID]', event['ResourceProperties']['DestinationColumnUserId'])
    script_template = script_template.replace('[S_EVENT_TYPE]', event['ResourceProperties']['SourceColumnEventType'])
    script_template = script_template.replace('[D_EVENT_TYPE]', event['ResourceProperties']['DestinationColumnEventType'])
    script_template = script_template.replace('[S_EVENT_VALUE]', event['ResourceProperties']['SourceColumnEventValue'])
    script_template = script_template.replace('[D_EVENT_VALUE]', event['ResourceProperties']['DestinationColumnEventValue'])
    script_template = script_template.replace('[S_TIME]', event['ResourceProperties']['SourceColumnTimestamp'])
    script_template = script_template.replace('[D_TIME]', event['ResourceProperties']['DestinationColumnTimestamp'])            
    script_template = script_template.replace('[DATABASE_NAME]', event['ResourceProperties']['DatabaseName'])
    script_template = script_template.replace('[TABLE_NAME]', event['ResourceProperties']['TableName'])
    script_template = script_template.replace('[OUTPUT_PATH]', 's3://{}{}'.format(event['ResourceProperties']['DestinationBucketName'], event['ResourceProperties']['DestinationDataPrefix']))

    script_bucket = os.environ['CONVERSION_JOB_SCRIPT_BUCKET']
    script_filename = 'conversionScript'

    try:
        if event['RequestType'] == 'Create':
            object = s3.Object(script_bucket, script_filename)
            object.put(Body=str.encode(script_template))
            response_data = {"Message": "Resource creation successful!", "Script": 's3://{}/{}'.format(script_bucket, script_filename)}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        elif event['RequestType'] == 'Update':
            object = s3.Object(script_bucket, script_filename)
            object.put(Body=str.encode(script_template))
            response_data = {"Message": "Resource creation successful!","Script": 's3://{}/{}'.format(script_bucket, script_filename)}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        elif event['RequestType'] == 'Delete':
            s3.Object(script_bucket, script_filename).delete()
            s3.Object(script_bucket, script_filename+'.temp').delete()
            response_data = {"Message": "Resource deletion successful!"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        else:
            response_data = {"Message": "Unexpected event received from CloudFormation"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)

    except Exception as error:         
        print(error)
        response_data = {"Message": "Unexpected error occured."}
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)