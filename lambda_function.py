import json
import boto3
import os

bedrock_agent_rt = boto3.client("bedrock-agent-runtime")
bedrock_rt = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

KB_ID = os.environ["KB_ID"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
table = dynamodb.Table("FaultHistory")

VIBRATION_THRESHOLD = 7.0
TEMP_THRESHOLD = 85.0


def detect_fault(vibration, temp):
    if vibration > VIBRATION_THRESHOLD:
        return "high vibration"
    if temp > TEMP_THRESHOLD:
        return "overheating"
    return None


def retrieve_sop(fault_type):
    resp = bedrock_agent_rt.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": fault_type}
    )
    chunks = [r["content"]["text"] for r in resp.get("retrievalResults", [])]
    return "\n".join(chunks) if chunks else "No SOP found."


def get_occurrence_count(machine_id, fault_type):
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
    return int(resp["Attributes"]["fault_counts"][fault_type])


def summarize_with_claude(machine_id, fault_type, sop_text, occurrence_count):
    prompt = f"""You are a plant maintenance assistant.
Machine: {machine_id}
Fault detected: {fault_type}
Times this fault has occurred this month: {occurrence_count}
Relevant SOP:
{sop_text}

Write a concise work order (3-4 sentences) including recommended action and whether this should be escalated to a senior technician."""

    response = bedrock_rt.invoke_model(
        modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def lambda_handler(event, context):
    machine_id = event["machine_id"]
    vibration = float(event["vibration_mm_s"])
    temp = float(event["temp_c"])

    fault = detect_fault(vibration, temp)
    if not fault:
        return {"status": "normal", "machine_id": machine_id}

    occurrence_count = get_occurrence_count(machine_id, fault)
    sop_text = retrieve_sop(fault)
    work_order = summarize_with_claude(machine_id, fault, sop_text, occurrence_count)

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"Work Order: {machine_id} - {fault}",
        Message=work_order
    )

    return {
        "status": "fault_detected",
        "machine_id": machine_id,
        "fault_type": fault,
        "occurrence_count": occurrence_count,
        "work_order": work_order
    }
