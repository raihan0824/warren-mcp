# Warren Finance MCP Server

Personal finance agent MCP server. Exposes read-only finance tools over HTTP, backed by PostgreSQL semantic views.

## Features

- **4 Finance Tools**:
  - `finance.get_spend_summary` - Total spend and transaction count
  - `finance.get_spend_by_category` - Spend breakdown per category
  - `finance.get_spend_by_merchant` - Top merchants by spend
  - `finance.get_recent_transactions` - Latest transactions

- **Time Ranges**: today, yesterday, this_week, last_week, this_month
- **Timezone**: Asia/Jakarta (UTC+7)
- **Transport**: Streamable HTTP (MCP protocol)

## Prerequisites

- Python 3.11+
- PostgreSQL with semantic views:
  - `v_tx_clean`
  - `v_spend_daily`
  - `v_spend_weekly`
  - `v_spend_by_category_daily`
  - `v_spend_by_merchant_daily`

## Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <repo-url>
   cd warren-mcp
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your DATABASE_URL
   ```

3. **Run the server**:
   ```bash
   python -m src.server
   ```

   Server starts at `http://localhost:8000/mcp`

## Usage with MCP Clients

### Claude Desktop / Claude Code

```bash
claude mcp add --transport http warren-finance http://localhost:8000/mcp
```

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector
# Connect to http://localhost:8000/mcp
```

## Docker

```bash
# Build
docker build -t warren-finance-mcp .

# Run
docker run -e DATABASE_URL=postgresql://... -p 8000:8000 warren-finance-mcp
```

## Kubernetes

```bash
# Create secret
kubectl create secret generic postgres-secret --from-literal=url=postgresql://...

# Deploy
kubectl apply -f k8s/
```

## API Examples

### Get Spend Summary
```json
// Tool: finance.get_spend_summary
// Input:
{"range": "today"}

// Output:
{
  "range": "today",
  "spend_total_rp": 150000,
  "tx_count": 3
}
```

### Get Spend by Category
```json
// Tool: finance.get_spend_by_category
// Input:
{"range": "this_week"}

// Output:
{
  "range": "this_week",
  "items": [
    {"category_code": "food", "category_name": "Food & Dining", "spend_total_rp": 500000, "tx_count": 10}
  ]
}
```

### Get Spend by Merchant
```json
// Tool: finance.get_spend_by_merchant
// Input:
{"range": "this_month", "limit": 5}

// Output:
{
  "range": "this_month",
  "items": [
    {"merchant": "Starbucks", "spend_total_rp": 200000, "tx_count": 5}
  ]
}
```

### Get Recent Transactions
```json
// Tool: finance.get_recent_transactions
// Input:
{"limit": 5}

// Output:
{
  "items": [
    {"datetime_jakarta": "2026-01-05 14:30:00", "merchant": "Starbucks", "category_code": "food", "total_rp": 50000}
  ]
}
```

## Error Handling

All tools return errors in this format:
```json
{
  "error": {
    "code": "INVALID_INPUT | INTERNAL_ERROR",
    "message": "human readable message"
  }
}
```

## License

MIT
