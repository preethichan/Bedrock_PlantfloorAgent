Sensor Event → Lambda (PlantFloorAgent)
                  ├─→ DynamoDB (FaultHistory) — fault occurrence tracking
                  ├─→ Bedrock Knowledge Base (S3 + OpenSearch Serverless) — SOP retrieval
                  ├─→ Bedrock Claude 3.5 Sonnet — work order generation + escalation logic
                  └─→ SNS (PlantFloorAlerts) — notify maintenance team
