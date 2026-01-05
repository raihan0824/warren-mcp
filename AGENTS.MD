Warren Finance MCP Server – Requirements, APIs, Deployment

Overview

Warren is a personal finance agent. This MCP server exposes read-only finance tools over HTTP, backed by PostgreSQL and semantic views. The LLM must never generate SQL. It must call tools only.

Primary goals:
	•	Answer questions like “how much did I spend today”
	•	Deterministic, auditable outputs
	•	Safe read-only access to finance data

Non-goals (v1):
	•	No DB writes
	•	No budgeting logic
	•	No forecasting or recommendations

⸻

Tech Stack
	•	Python 3.11+
	•	MCP Python SDK
	•	HTTP transport (not stdio)
	•	Timezone: Asia/Jakarta

⸻

Database Assumptions

Existing tables:
	•	transactions
	•	categories
	•	pending_verifications

Semantic views (required):
	•	v_tx_clean
	•	v_spend_daily
	•	v_spend_weekly
	•	v_spend_by_category_daily
	•	v_spend_by_merchant_daily

All views already filter to successful transactions only.

⸻

Server Responsibilities
	•	Expose finance data as MCP tools
	•	Read-only access only
	•	Parameterized queries only
	•	No schema leakage
	•	JSON responses only

⸻

Time Handling

Supported ranges:
	•	today
	•	yesterday
	•	this_week
	•	last_week
	•	this_month

Rules:
	•	Compute start_ts and end_ts in Python using Asia/Jakarta
	•	Pass timestamps as query parameters

⸻

Tools

All tools are prefixed with finance.

finance.get_spend_summary

Description:
	•	Total spend and transaction count

Input schema:

{
  "type": "object",
  "required": ["range"],
  "properties": {
    "range": {
      "type": "string",
      "enum": ["today", "yesterday", "this_week", "last_week", "this_month"]
    }
  }
}

Output schema:

{
  "type": "object",
  "required": ["range", "spend_total_rp", "tx_count"],
  "properties": {
    "range": { "type": "string" },
    "spend_total_rp": { "type": "number" },
    "tx_count": { "type": "number" }
  }
}

Data source:
	•	v_spend_daily
	•	v_spend_weekly

⸻

finance.get_spend_by_category

Description:
	•	Spend breakdown per category

Input schema:

{
  "type": "object",
  "required": ["range"],
  "properties": {
    "range": {
      "type": "string",
      "enum": ["today", "this_week", "this_month"]
    }
  }
}

Output schema:

{
  "type": "object",
  "required": ["range", "items"],
  "properties": {
    "range": { "type": "string" },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "category_code": { "type": "string" },
          "category_name": { "type": "string" },
          "spend_total_rp": { "type": "number" },
          "tx_count": { "type": "number" }
        }
      }
    }
  }
}

Data source:
	•	v_spend_by_category_daily

⸻

finance.get_spend_by_merchant

Description:
	•	Top merchants by spend

Input schema:

{
  "type": "object",
  "required": ["range"],
  "properties": {
    "range": {
      "type": "string",
      "enum": ["today", "this_week", "this_month"]
    },
    "limit": {
      "type": "number",
      "default": 5
    }
  }
}

Output schema:

{
  "type": "object",
  "required": ["range", "items"],
  "properties": {
    "range": { "type": "string" },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "merchant": { "type": "string" },
          "spend_total_rp": { "type": "number" },
          "tx_count": { "type": "number" }
        }
      }
    }
  }
}

Data source:
	•	v_spend_by_merchant_daily

⸻

finance.get_recent_transactions

Description:
	•	Latest transactions

Input schema:

{
  "type": "object",
  "properties": {
    "limit": { "type": "number", "default": 5 }
  }
}

Output schema:

{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "datetime_jakarta": { "type": "string" },
          "merchant": { "type": "string" },
          "category_code": { "type": "string" },
          "total_rp": { "type": "number" }
        }
      }
    }
  }
}

Data source:
	•	v_tx_clean

⸻

Error Format

{
  "error": {
    "code": "INVALID_INPUT | INTERNAL_ERROR",
    "message": "human readable message"
  }
}


⸻

Deployment

Docker

Dockerfile:

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

Kubernetes

Deployment:

apiVersion: apps/v1
kind: Deployment
metadata:
  name: warren-finance-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: warren-finance-mcp
  template:
    metadata:
      labels:
        app: warren-finance-mcp
    spec:
      containers:
      - name: server
        image: warren-finance-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url

Service:

apiVersion: v1
kind: Service
metadata:
  name: warren-finance-mcp
spec:
  selector:
    app: warren-finance-mcp
  ports:
  - port: 80
    targetPort: 8000


⸻

Definition of Done
	•	MCP server runs over HTTP
	•	Tools are discoverable
	•	Claude / Cursor can call tools
	•	Question “how much did I spend today” works end-to-end
	•	No hallucinated data