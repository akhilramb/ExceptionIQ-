# ExceptionIQ

ExceptionIQ is a financial exception investigation system that turns approved resolutions into reusable organizational memory. New invoice/PO exceptions are compared with historical cases, recommendations are grounded in that evidence, and a human decides whether to approve the resolution before it becomes new memory.

## Core workflow

1. Create an exception with vendor, invoice/PO amounts, type and context.
2. ExceptionIQ calculates the variance and retrieves similar historical cases.
3. The investigation ranks memories using vendor, problem type, amount proximity and successful outcomes.
4. The UI shows the likely root cause, recommended action, evidence cases and confidence.
5. A human reviews the evidence and approves the resolution.
6. Approved resolutions are stored as new organizational memory and influence later cases.

ExceptionIQ deliberately does **not** invent a precedent when no useful memory exists; it falls back to manual verification.

## Features

- Responsive exception intelligence dashboard
- Create and investigate invoice/PO exceptions
- Evidence-ranked historical case retrieval
- Confidence and evidence count for recommendations
- Human-in-the-loop approval
- Automatic learning from approved resolutions
- Memory Explorer
- Resolution and memory analytics
- Health endpoint and API documentation
- SQLite persistence with idempotent demo seeding
- Automated backend tests with GitHub Actions
- Environment-based runtime configuration

## Technology

- Frontend: React 18 loaded from CDN, JavaScript, CSS
- Backend: Python, FastAPI, Pydantic
- Persistence: SQLite
- Memory layer: local Hindsight-compatible case store
- Testing: pytest + FastAPI TestClient
- CI: GitHub Actions

The current core build uses deterministic, evidence-grounded recommendation logic. `OPENAI_API_KEY` is reserved in configuration for an optional provider integration; the project does not claim that a live external LLM or Hindsight SaaS service is active unless those integrations are explicitly configured.

## Quick start

```bash
git clone https://github.com/akhilramb/ExceptionIQ-.git
cd ExceptionIQ-/backend
python -m venv .venv
```

Activate the virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
python main.py
```

Open `http://127.0.0.1:8000`.

FastAPI documentation is available at `http://127.0.0.1:8000/docs`.

## Tests

From `backend/`:

```bash
pytest -q
```

The repository also runs these tests in `.github/workflows/test.yml`.

## API

- `GET /api/health` — runtime health/provider status
- `GET /api/exceptions` — list exceptions
- `GET /api/exceptions/{id}` — exception details
- `POST /api/exceptions` — create an exception
- `PATCH /api/exceptions/{id}` — update an exception
- `POST /api/exceptions/{id}/resolve` — approve/reject and optionally learn the resolution
- `POST /api/investigate` — retrieve evidence and generate a grounded recommendation
- `GET /api/memories` — list organizational memories
- `POST /api/memories` — add a memory
- `GET /api/analytics` — resolution, memory and vendor/type metrics

## Configuration

Copy `.env.example` values into your environment as needed. Do not commit secrets.

- `HOST` — server bind address
- `PORT` — server port
- `CORS_ORIGINS` — comma-separated allowed origins
- `OPENAI_API_KEY` — optional placeholder for a future/live provider integration

## Project structure

```text
ExceptionIQ-/
├── .github/workflows/test.yml
├── .env.example
├── frontend/
│   ├── index.html
│   ├── App.js
│   └── styles.css
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── api/routes.py
│   ├── models/database.py
│   └── tests/test_api.py
└── README.md
```

## Demo case

A useful demo is:

```text
Vendor: NovaTech Solutions
Invoice amount: ₹106,500
PO amount: ₹100,000
Exception type: Invoice Amount Mismatch
```

The seeded memory includes a related ₹6,500 freight-charge case, allowing the investigation view to demonstrate similarity retrieval, evidence, confidence, approval and learning.

## Important design principle

ExceptionIQ is decision support, not autonomous financial approval. Recommendations should be reviewed against the invoice, purchase order, contract terms and supporting documents before action is taken.
