# Mental Wellness API (FastAPI + MongoDB)

## Quick start (local)
1. Copy `.env.example` to `.env` and fill in your MongoDB URI, JWT secret, Stripe, and OpenAI keys.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `python run.py`.
4. Open Swagger UI at `http://localhost:8000/docs`.
5. Health check: `GET http://localhost:8000/health`.

## Quick start (Docker)
1. Update `.env`.
2. Run `docker-compose up --build`.
3. Open Swagger UI at `http://localhost:8000/docs`.

## Example requests

### Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"StrongPass123"}'
```

### Login (OAuth2 form)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=StrongPass123"
```

### Create journal entry
```bash
curl -X POST http://localhost:8000/api/v1/journals \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Gratitude","content":"Today I am grateful for...","category":"gratitude","entry_date":"2026-02-09"}'
```

### Filter journal by date
```bash
curl -X GET "http://localhost:8000/api/v1/journals?start_date=2026-02-01&end_date=2026-02-09" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Save mood
```bash
curl -X POST http://localhost:8000/api/v1/moods \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mood":"good","intensity":7,"notes":"Calm day","entry_date":"2026-02-09"}'
```

### AI chat (premium)
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Give me a calming exercise"}]}'
```

### Create Stripe checkout session
```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/checkout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"premium"}'
```
