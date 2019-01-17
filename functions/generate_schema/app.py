import json
import boto3
import os
import cfnresponse

def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    try:
        if event['RequestType'] == 'Create':
            response_data = {"Message": "Resource creation successful!"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        elif event['RequestType'] == 'Update':
            response_data = {"Message": "Resource creation successful!"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        elif event['RequestType'] == 'Delete':
            response_data = {"Message": "Resource deletion successful!"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        else:
            response_data = {"Message": "Unexpected event received from CloudFormation"}
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)

    except Exception as error:         
        print(error)
        response_data = {"Message": "Unexpected error occured."}
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data)