import json
import boto3
from decimal import Decimal
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("BioBandReadings")

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "bioband-raw-data-shivsharma2026"

def lambda_handler(event, context):
    """
    Triggered with a sensor reading (event).
    Writes it into DynamoDB, and archives the raw JSON into S3.
    """
    # --- DynamoDB write (existing logic) ---
    item = json.loads(json.dumps(event), parse_float=Decimal)
    table.put_item(Item=item)

    # --- S3 archive (new) ---
    device_id = event.get("device_id", "unknown-device")
    timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())
    # Make the timestamp filesystem-safe (colons aren't allowed in S3 keys on some clients)
    safe_timestamp = timestamp.replace(":", "-")
    s3_key = f"raw-readings/{device_id}/{safe_timestamp}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(event),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(f"Stored reading for {device_id} at {timestamp} (DynamoDB + S3)")
    }