#!/bin/bash

set -e

echo "Creating OMS LocalStack resources..."

REGION="us-east-1"
ACCOUNT_ID="000000000000"

TOPIC_NAME="order-created"

ERP_QUEUE_NAME="order-erp-queue"
ERP_DLQ_NAME="order-erp-dlq"

NOTIFICATION_QUEUE_NAME="order-notification-queue"
NOTIFICATION_DLQ_NAME="order-notification-dlq"


echo "Creating SNS topic..."

awslocal sns create-topic \
  --name "$TOPIC_NAME"


echo "Creating dead-letter queues..."

awslocal sqs create-queue \
  --queue-name "$ERP_DLQ_NAME"

awslocal sqs create-queue \
  --queue-name "$NOTIFICATION_DLQ_NAME"


echo "Creating main queues..."

awslocal sqs create-queue \
  --queue-name "$ERP_QUEUE_NAME"

awslocal sqs create-queue \
  --queue-name "$NOTIFICATION_QUEUE_NAME"


TOPIC_ARN="arn:aws:sns:${REGION}:${ACCOUNT_ID}:${TOPIC_NAME}"

ERP_QUEUE_ARN="arn:aws:sqs:${REGION}:${ACCOUNT_ID}:${ERP_QUEUE_NAME}"
ERP_DLQ_ARN="arn:aws:sqs:${REGION}:${ACCOUNT_ID}:${ERP_DLQ_NAME}"

NOTIFICATION_QUEUE_ARN="arn:aws:sqs:${REGION}:${ACCOUNT_ID}:${NOTIFICATION_QUEUE_NAME}"
NOTIFICATION_DLQ_ARN="arn:aws:sqs:${REGION}:${ACCOUNT_ID}:${NOTIFICATION_DLQ_NAME}"

ERP_QUEUE_URL="http://sqs.${REGION}.localhost.localstack.cloud:4566/${ACCOUNT_ID}/${ERP_QUEUE_NAME}"

NOTIFICATION_QUEUE_URL="http://sqs.${REGION}.localhost.localstack.cloud:4566/${ACCOUNT_ID}/${NOTIFICATION_QUEUE_NAME}"


echo "Creating redrive policy files..."

cat > /tmp/erp-redrive.json <<EOF
{
  "RedrivePolicy": "{\"deadLetterTargetArn\":\"${ERP_DLQ_ARN}\",\"maxReceiveCount\":\"3\"}"
}
EOF

cat > /tmp/notification-redrive.json <<EOF
{
  "RedrivePolicy": "{\"deadLetterTargetArn\":\"${NOTIFICATION_DLQ_ARN}\",\"maxReceiveCount\":\"3\"}"
}
EOF


echo "Configuring ERP redrive policy..."

awslocal sqs set-queue-attributes \
  --queue-url "$ERP_QUEUE_URL" \
  --attributes file:///tmp/erp-redrive.json


echo "Configuring notification redrive policy..."

awslocal sqs set-queue-attributes \
  --queue-url "$NOTIFICATION_QUEUE_URL" \
  --attributes file:///tmp/notification-redrive.json


echo "Subscribing ERP queue to SNS..."

awslocal sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol sqs \
  --notification-endpoint "$ERP_QUEUE_ARN" \
  --attributes RawMessageDelivery=true


echo "Subscribing notification queue to SNS..."

awslocal sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol sqs \
  --notification-endpoint "$NOTIFICATION_QUEUE_ARN" \
  --attributes RawMessageDelivery=true


echo "OMS LocalStack initialization complete."