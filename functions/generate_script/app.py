 # Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this
 # software and associated documentation files (the "Software"), to deal in the Software
 # without restriction, including without limitation the rights to use, copy, modify,
 # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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

    # Create Column Mappings
    map_item_id = '("{}", "int", "{}", "int")'.format(event['ResourceProperties']['SourceColumnItemId'], event['ResourceProperties']['DestinationColumnItemId'])
    map_user_id = '("{}", "int", "{}", "int")'.format(event['ResourceProperties']['SourceColumnUserId'], event['ResourceProperties']['DestinationColumnUserId'])
    map_event_type = '("{}", "string", "{}", "string")'.format(event['ResourceProperties']['SourceColumnEventType'], event['ResourceProperties']['DestinationColumnEventType'])
    map_event_value = '("{}", "int", "{}", "int")'.format(event['ResourceProperties']['SourceColumnEventValue'], event['ResourceProperties']['DestinationColumnEventValue'])
    map_timestamp = '("{}", "int", "{}", "int")'.format(event['ResourceProperties']['SourceColumnTimestamp'], event['ResourceProperties']['DestinationColumnTimestamp'])

    # Setup Column Mappings based on PersonalizeDatasetName (User, Item, Interactions)
    if event['ResourceProperties']['PersonalizeDatasetName'] == "User":
        column_mappings = '{}'.format(map_user_id)
    elif event['ResourceProperties']['PersonalizeDatasetName'] == "Item":
        column_mappings = '{}'.format(map_item_id)
    else: 
        # Map all if not User/Item
        column_mappings = '{},{},{},{},{}'.format(map_item_id, map_user_id, map_event_type, map_event_value, map_timestamp)

    # Replace Column Mappings in Template
    script_template = script_template.replace('[COLUMN_MAPPINGS]', column_mappings)

    # Replace Template Placeholder Values with ResourceProperties          
    script_template = script_template.replace('[DATABASE_NAME]', event['ResourceProperties']['DatabaseName'])
    script_template = script_template.replace('[TABLE_NAME]', event['ResourceProperties']['TableName'])
    script_template = script_template.replace('[OUTPUT_PATH]', 's3://{}{}'.format(event['ResourceProperties']['DestinationBucketName'], event['ResourceProperties']['DestinationDataPrefix']))

    # Output Location Details
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