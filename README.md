# Personal Finance Autopilot

Production-minded MVP for the PRD and plan in this repository.

It includes:

- FastAPI backend with JWT auth, SQLAlchemy models, PDF/CSV/Excel import, parser registry, deduplication, categorization, subscriptions, bills, alerts, cashflow, and safe-to-spend logic.
- Next.js frontend with dashboard, import flow, transactions, subscriptions, bills, alerts, settings, login, signup, and demo data login.
- SQLite by default for immediate local development, PostgreSQL-ready through `DATABASE_URL`.

## Quick Start

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

Demo login:

```text
demo@example.com
demo1234
```

## PostgreSQL

Start a local database:

```bash
docker compose up -d postgres
```

Use this backend `DATABASE_URL`:

```text
postgresql://finance:finance@localhost:5432/personal_finance_autopilot
```

## API

Backend runs under:

```text
http://localhost:8000/api/v1
```

Core routes:

- `POST /auth/signup`
- `POST /auth/login`
- `GET /dashboard?month=YYYY-MM`
- `POST /import/upload`
- `POST /import/uploads/{upload_id}/confirm`
- `GET /transactions`
- `GET /subscriptions`
- `GET /bills`
- `GET /alerts`
- `GET /settings`

## Import Samples

The `sample_data/` folder has Google Pay, PhonePe, and bank statement CSVs you can upload through the Import page. The import flow also accepts text-based PDFs and an optional PDF password; scanned/image-only PDFs return a preview warning until OCR is added.

## Notes

For speed, the MVP uses `Base.metadata.create_all()` on startup. The models are structured for Alembic migrations, and the next production hardening step should be adding migration revisions before deployment.
