#!/bin/bash
set -e

BUCKET="plant-floor-agent-preethi-2026"
REGION="us-east-1"

aws s3 mb s3://$BUCKET --region $REGION
aws s3 cp sop/ s3://$BUCKET/sop/ --recursive

aws dynamodb create-table \
  --table-name FaultHistory \
  --attribute-definitions AttributeName=machine_id,AttributeType=S \
  --key-schema AttributeName=machine_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION

aws sns create-topic --name PlantFloorAlerts --region $REGION

echo "Bucket, table, and topic created."
echo "Next: create Bedrock Knowledge Base via console pointing at s3://$BUCKET/sop/"
echo "Then create Lambda function 'PlantFloorAgent' and deploy lambda_function.py"
