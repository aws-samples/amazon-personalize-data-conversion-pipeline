import json
import boto3
import os
import cfnresponse

def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    # Schema Template for Personalize Import
    schema_template = ""

    # Read Schema Template
    schema_template_file = os.environ['LAMBDA_TASK_ROOT'] + '/schema.template'
    with open(schema_template_file, 'r') as template_file:
        schema_template=json.loads(template_file.read())

    # Set Record Name
    schema_template['name'] = event['ResourceProperties']['PersonalizeDatasetName']

    # Add Fields to Schema Template
    if event['ResourceProperties']['DestinationColumnItemId']:

        field = {
            'name': event['ResourceProperties']['DestinationColumnItemId'],
            'type': 'string'
        }

        schema_template['fields'].append(field)

    if event['ResourceProperties']['DestinationColumnUserId']:

        field = {
                'name': event['ResourceProperties']['DestinationColumnUserId'],
                'type': 'string'
            }
        
        schema_template['fields'].append(field)

    if event['ResourceProperties']['DestinationColumnEventType']:

        field = {
                'name': event['ResourceProperties']['DestinationColumnEventType'],
                'type': 'string'
            }

        schema_template['fields'].append(field)

    if event['ResourceProperties']['DestinationColumnEventValue']:

        field = {
                'name': event['ResourceProperties']['DestinationColumnEventValue'],
                'type': 'string'
            }

        schema_template['fields'].append(field)

    if event['ResourceProperties']['DestinationColumnTimestamp']:

        field = {
                'name': event['ResourceProperties']['DestinationColumnTimestamp'],
                'type': 'long'
            }

        schema_template['fields'].append(field)

    # Output Location Details
    schema_bucket = os.environ['CONVERSION_JOB_SCHEMA_BUCKET']
    schema_filename = 'schema.json'

    try:
        if event['RequestType'] == 'Create':
            object = s3.Object(schema_bucket, schema_filename)
            object.put(Body=str.encode(json.dumps(schema_template, indent=4)))
            response_data = {"Message": "Resource creation successful!", "Schema": 's3://{}/{}'.format(schema_bucket, schema_filename)}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        elif event['RequestType'] == 'Update':
            object = s3.Object(schema_bucket, schema_filename)
            object.put(Body=str.encode(json.dumps(schema_template, indent=4)))
            response_data = {"Message": "Resource creation successful!", "Schema": 's3://{}/{}'.format(schema_bucket, schema_filename)}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        elif event['RequestType'] == 'Delete':
            s3.Object(schema_bucket, schema_filename).delete()
            s3.Object(schema_bucket, schema_filename+'.temp').delete()
            response_data = {"Message": "Resource deletion successful!"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        else:
            response_data = {"Message": "Unexpected event received from CloudFormation"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)

    except Exception as error:         
        print(error)
        response_data = {"Message": "Unexpected error occured."}
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)