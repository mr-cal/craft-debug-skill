# Reference Documentation for Craft Debug V2

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

## When Reference Docs Are Useful

Reference docs are ideal for:
- **Comprehensive guides** - Multi-page documentation that would bloat SKILL.md
- **API documentation** - Endpoint specifications, parameters, examples
- **Schemas** - Database schemas, data models, type definitions
- **Domain knowledge** - Company policies, industry standards, legal templates
- **Detailed workflows** - Step-by-step procedures with screenshots/diagrams

## Structure Suggestions

Choose a structure that fits your content:

### API Reference Example
```markdown
## Authentication
- Method: Bearer token
- Header: `Authorization: Bearer <token>`

## Endpoints

### GET /api/users
**Description:** Retrieve user list
**Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Results per page (default: 20)

**Response:**
\`\`\`json
{
  "users": [...],
  "total": 150,
  "page": 1
}
\`\`\`

**Error codes:**
- 401: Unauthorized
- 429: Rate limit exceeded
```

### Workflow Guide Example
```markdown
## Prerequisites
- Python 3.8+
- API credentials configured
- Required packages: `pip install -r requirements.txt`

## Step 1: Initialize Connection
1. Import the client: `from myapi import Client`
2. Create instance: `client = Client(api_key='...')`
3. Test connection: `client.ping()`

## Step 2: Fetch Data
[Detailed instructions...]

## Troubleshooting
**Problem:** Connection timeout
**Solution:** Check firewall settings...
```

### Schema Documentation Example
```markdown
## Database Schema

### Table: users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique user ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| created_at | TIMESTAMP | DEFAULT NOW() | Registration time |

### Relationships
- users.id → orders.user_id (one-to-many)
- users.id → profiles.user_id (one-to-one)
```

## Tips for Large Reference Files

If this file will be >100 lines:
- Include a **Table of Contents** at the top
- Use clear section headers (##, ###)
- Add grep hints in main SKILL.md for easier navigation

## Best Practices

✅ **DO:**
- Keep SKILL.md lean, move details here
- Use tables for structured data
- Include concrete examples
- Link back to SKILL.md where relevant

❌ **DON'T:**
- Duplicate content from SKILL.md
- Create reference docs for <50 lines of content (put in SKILL.md)
- Use vague descriptions (be specific)
- Forget to mention this file exists in SKILL.md
