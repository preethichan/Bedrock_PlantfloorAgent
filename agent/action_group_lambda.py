import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("FaultHistory")


def create_work_order(machine_id, fault_type, severity):
    table.update_item(
        Key={"machine_id": machine_id},
        UpdateExpression="SET fault_counts = if_not_exists(fault_counts, :empty)",
        ExpressionAttributeValues={":empty": {}}
    )
    resp = table.update_item(
        Key={"machine_id": machine_id},
        UpdateExpression="SET fault_counts.#f = if_not_exists(fault_counts.#f, :zero) + :one",
        ExpressionAttributeNames={"#f": fault_type},
        ExpressionAttributeValues={":zero": 0, ":one": 1},
        ReturnValues="UPDATED_NEW"
    )
    count = int(resp["Attributes"]["fault_counts"][fault_type])
    return {
        "work_order_id": f"WO-{machine_id}-{fault_type}".replace(" ", "-"),
        "machine_id": machine_id,
        "fault_type": fault_type,
        "severity": severity,
        "occurrence_count": count,
        "status": "CREATED"
    }


def check_fault_history(machine_id, fault_type):
    resp = table.get_item(Key={"machine_id": machine_id})
    item = resp.get("Item", {})
    count = item.get("fault_counts", {}).get(fault_type, 0)
    return {"machine_id": machine_id, "fault_type": fault_type, "occurrence_count": int(count)}


def lambda_handler(event, context):
    api_path = event["apiPath"]
    http_method = event["httpMethod"]
    params = {}

    if http_method == "GET":
        for p in event.get("parameters", []):
            params[p["name"]] = p["value"]
    else:
        body = event["requestBody"]["content"]["application/json"]["properties"]
        for p in body:
            params[p["name"]] = p["value"]

    if api_path == "/create-work-order":
        result = create_work_order(params["machine_id"], params["fault_type"], params["severity"])
    elif api_path == "/check-fault-history":
        result = check_fault_history(params["machine_id"], params["fault_type"])
    else:
        result = {"error": "unknown path"}

    response_body = {"application/json": {"body": json.dumps(result)}}

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": 200,
            "responseBody": response_body
        }
    }
