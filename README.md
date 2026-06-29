# Plant Floor Agent — AWS Bedrock Predictive Maintenance

Real AWS Bedrock-based agentic pipeline for industrial fault triage, built for
Automotive & Manufacturing use cases.

## Architecture
- **S3**: stores maintenance SOP documents
- **Amazon Bedrock Knowledge Base** (OpenSearch Serverless vector store): RAG retrieval over SOPs
- **AWS Lambda**: orchestrates fault detection, KB retrieval, and reasoning
- **Amazon Bedrock (Claude 3.5 Sonnet)**: generates the work order summary and escalation decision
- **DynamoDB**: tracks recurring faults per machine (acts as agent "memory")
- **SNS**: delivers the generated work order to maintenance staff

## Flow
1. Sensor reading (vibration/temp) is sent to Lambda
2. Lambda detects fault type via threshold rule
3. Increments fault occurrence count in DynamoDB
4. Retrieves the matching SOP from the Bedrock Knowledge Base
5. Claude 3.5 Sonnet generates a work order, deciding whether to escalate based on recurrence and severity
6. Work order is published via SNS

## Part 2: Native Bedrock Agent (in progress)

Upgraded the architecture from a single orchestrating Lambda to a native
**Amazon Bedrock Agent** that owns the reasoning loop itself:

- Agent (Claude Sonnet 4.5) interprets the request and decides which tools to call
- Knowledge Base association for automatic SOP retrieval
- Action group (Lambda) exposing `createWorkOrder` and `checkFaultHistory` as
  callable tools, defined via OpenAPI schema (`agent/action-group-schema.json`)

This shifts orchestration logic from hardcoded Python control flow into the
agent's own planning — the architectural difference between "an app that calls
an LLM" and "an actual agent."

Status: action group + knowledge base wired and tested; finishing AWS Marketplace
billing verification for full model invocation.
