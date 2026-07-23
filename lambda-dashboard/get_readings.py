import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("BioBandReadings")

class DecimalEncoder(json.JSONEncoder):
    """DynamoDB returns Decimal objects — this converts them back to normal numbers for JSON."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    """
    Returns the most recent readings for bioband-001, sorted by time.
    Triggered via API Gateway (HTTP request), not IoT Core.
    """
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("device_id").eq("bioband-001"),
        ScanIndexForward=False,  # newest first
        Limit=50
    )

    items = response.get("Items", [])
    items.reverse()  # so the chart displays oldest → newest, left to right

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # allows our webpage to call this from the browser
            "Content-Type": "application/json"
        },
        "body": json.dumps(items, cls=DecimalEncoder)
    }