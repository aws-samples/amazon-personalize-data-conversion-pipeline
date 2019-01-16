import json
import boto3
import os
import cfnresponse

def lambda_handler(event, context):

    s3 = boto3.resource('s3')

    script_template = """import sys
    from awsglue.transforms import *
    from awsglue.utils import getResolvedOptions
    from pyspark.context import SparkContext
    from awsglue.context import GlueContext
    from awsglue.job import Job
    from awsglue.dynamicframe import DynamicFrame
    args = getResolvedOptions(sys.argv, ['JOB_NAME'])
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)
    datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "[DATABASE_NAME]", table_name = "[TABLE_NAME]", transformation_ctx = "datasource0")
    applymapping1 = ApplyMapping.apply(frame = datasource0, mappings = [("[S_ITEM_ID]", "int", "[D_ITEM_ID]", "int"), ("[S_USER_ID]", "int", "[D_USER_ID]", "int"), ("[S_EVENT_TYPE]", "string", "[D_EVENT_TYPE]", "string"), ("[S_EVENT_VAL]", "int", "[D_EVENT_VAL]", "int"), ("[S_TIME]", "int", "[D_TIME]", "int"), transformation_ctx = "applymapping1")
    repartitioned_df = applymapping1.toDF().repartition(1)
    repartitioned_dynf = DynamicFrame.fromDF(repartitioned_df, glueContext, "nested")
    datasink2 = glueContext.write_dynamic_frame.from_options(frame = repartitioned_dynf, connection_type = "s3", connection_options = {"path": "[OUTPUT_PATH]"}, format = "csv", transformation_ctx = "datasink2")
    job.commit()
    """

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

    print(script_template)

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