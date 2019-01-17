# Data Conversion Pipeline for Amazon Personalize

This template will deploy a sample data-conversion pipeline to convert data into the format required for training Amazon Personalize (ie: .CSV). Using the parmeters outlined below, you can customize this pipeline to convert data from various source formats into the formats required for Amazon Personalize User, Item, and Interaction data-sets.

Data will be cataloged with a Glue Crawler, and transformed with a Glue Job. The functions deployed as part of this solution are CloudFormation Custom Resources that will generate a data conversion script based on the cataloged source data, and provide example AVRO schema files you can use to train your Amazon Personalize solution.

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

## Source Data Format

This solution will create a glue-crawler that will crawl the provided S3 bucket and prefix for data. Example data could be JSON objects representing click-stream events delivered via an AWS Kinesis Firehose Delivery Stream. 

### Source Bucket Structure

s3://bucket_name/useritem/year/month/day/hour/file.json

### Source Data Example

```bash
{"type": "useritem", "ITEM_ID": 35, "USER_ID": 1, "EVENT_TYPE": "click", 
"EVENT_VALUE": 35, "TIMESTAMP": 1547159644}{"type": "useritem", "ITEM_ID": 34, 
"USER_ID": 1, "EVENT_TYPE": "click", "EVENT_VALUE": 34, "TIMESTAMP": 1547159646}
{"type": "useritem", "ITEM_ID": 29, "USER_ID": 1, "EVENT_TYPE": "click", 
"EVENT_VALUE": 29, "TIMESTAMP": 1547159648}{"type": "useritem", "ITEM_ID": 25, 
"USER_ID": 1, "EVENT_TYPE": "click", "EVENT_VALUE": 25, "TIMESTAMP": 1547159652}
{"type": "useritem", "ITEM_ID": 32, "USER_ID": 1, "EVENT_TYPE": "click", 
"EVENT_VALUE": 32, "TIMESTAMP": 1547159654}{"type": "useritem", "ITEM_ID": 22, 
"USER_ID": 1, "EVENT_TYPE": "click", "EVENT_VALUE": 22, "TIMESTAMP": 1547159656}
{"type": "useritem", "ITEM_ID": 25, "USER_ID": 1, "EVENT_TYPE": "click", 
"EVENT_VALUE": 25, "TIMESTAMP": 1547159658}{"type": "useritem", "ITEM_ID": 16, 
"USER_ID": 1, "EVENT_TYPE": "click", "EVENT_VALUE": 16, "TIMESTAMP": 1547159660}
{"type": "useritem", "ITEM_ID": 19, "USER_ID": 1, "EVENT_TYPE": "click", 
"EVENT_VALUE": 19, "TIMESTAMP": 1547159662}{"type": "useritem", "ITEM_ID": 18, 
"USER_ID": 1, "EVENT_TYPE": "click", "EVENT_VALUE": 18, "TIMESTAMP": 1547159665}
{"type": "useritem", "ITEM_ID": 4, "USER_ID": 1, "EVENT_TYPE": "click", 
"EVENT_VALUE": 4, "TIMESTAMP": 1547159668}{"type": "useritem", "ITEM_ID": 7, 
"USER_ID": 1, "EVENT_TYPE": "click", "EVENT_VALUE": 7, "TIMESTAMP": 1547159671}
```

## Output Data Format

This solution will run a Glue Job against the source data to generate a repartitioned .CSV file containing all of the records located in your source data bucket. This data is formatted in the way that Amazon Personalize required in order to import data into your DataSet Group.

### Output Bucket Structure

s3://bucket_name/converted/file.csv

### Output Data Example

```bash
ITEM_ID,USER_ID,EVENT_TYPE,EVENT_VALUE,TIMESTAMP
11,1,click,11,1547157950
35,1,click,35,1547159644
34,1,click,34,1547159646
29,1,click,29,1547159648
25,1,click,25,1547159652
32,1,click,32,1547159654
22,1,click,22,1547159656
25,1,click,25,1547159658
16,1,click,16,1547159660
19,1,click,19,1547159662
18,1,click,18,1547159665
4,1,click,4,1547159668
7,1,click,7,1547159671
```