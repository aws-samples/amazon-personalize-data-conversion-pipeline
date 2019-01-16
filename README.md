# Data Conversion Pipeline for Amazon Personalize

This template will deploy a sample data-conversion pipeline to convert data into the format required for training Amazon Personalize (ie: .CSV).

## Limitations

1. This solution only supports the most basic columns required to train Amazon Personalize. To add additional columns you would need to extend the template and the transformtion job script.

## Roadmap

1. Better handling of additional columns.
2. Annotations in Glue job to better explain each step.
3. Generate an example Avro schema for each output data set based on columns.
4. Better handling of column exclusions (currently adds empty data to output .CSV)

## Deployment

### Prerequisites

1. Install the AWS Serverless Application Model CLI - https://aws.amazon.com/serverless/sam/
2. Configure your local AWS Credentials (aws configure).
3. Create an S3 bucket to store the packaged code and replace S3_BUCKET_TO_STAGE_CODE with the name of your bucket in the comamands below. 
4. This solution assumes that you have source data located in S3 and partitioned by data type (ie: item, user, user-item interactions).

### Building the project

AWS CLI commands to package, deploy and describe outputs defined within the cloudformation stack:

```bash

sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket S3_BUCKET_TO_STAGE_CODE

sam deploy \
    --template-file packaged.yaml \
    --stack-name glue-personalize-converter \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides MyParameterSample=MySampleValue

aws cloudformation describe-stacks \
    --stack-name glue-personalize-converter --query 'Stacks[].Outputs'
```

## Parameters

* SourceBucketName - Name of the S3 Bucket where the source data exists.
* SourceDataPrefix - Name of the Prefix that contains the source data (ie: /user, /item, /interactions).
* DestinationBucketName - Name of the S3 Bucket where converted data should be stored.
* DestinationDataPrefix - Name of the Prefix that should contain the converted data.
* TableName - Name of the Table that will contain the converted data, typically the same as source prefix (ie: user, item, interactions)
* SourceColumnUserId - Source data column name for User ID.
* SourceColumnItemId - Source data column name for Item ID.
* SourceColumnEventType -Source data column name for Event Type.
* SourceColumnEventValue - Source data column name for Event Value.
* SourceColumnTimestamp - Source data column name for Event Timestamp.
* DestinationColumnUserId - Destination data column name for User ID.
* DestinationColumnItemId - Destination data column name for Item ID.
* DestinationColumnEventType - Destination data column name for Event Type.
* DestinationColumnEventValue - Destination data column name for Event Value.
* DestinationColumnTimestamp - Destination data column name for Event Timestamp.