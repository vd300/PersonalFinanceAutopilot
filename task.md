# TASK: Personal Finance Autopilot

## 1. Purpose of This File

This file breaks the project into small, executable tasks for Codex or any AI coding agent.

The goal is to avoid giving the AI one huge instruction like:

```text
Build the entire Personal Finance Autopilot app.
```

That creates too much context, too much ambiguity, and too many opportunities for the AI to make wrong assumptions.

Instead, each task should be small, clear, testable, and connected to the larger architecture.

---

## 2. Why We Need task.md

The project already has:

```text
prd.md
plan.md
task.md
```

Each document has a different purpose.

### prd.md

Explains what the product is, who it is for, what problems it solves, what features it needs, and what the MVP should include.

Use `prd.md` when you want Codex to understand the product.

### plan.md

Explains system architecture, backend/frontend structure, database strategy, parser architecture, API design, deployment plan, and extension strategy.

Use `plan.md` when you want Codex to understand how the system should be built.

### task.md

Explains what to build next, in what order, what files/modules to touch, what acceptance criteria must pass, and what not to modify.

Use `task.md` when you want Codex to implement one step at a time.

---

## 3. Does task.md Reduce Token Usage and AI Overhead?

Yes, if used correctly.

It helps reduce:

- Token usage
- Context overhead
- Repeated explanations
- Confusion
- Rework
- Memory burden on the AI
- Risk of Codex changing unrelated files

Instead of sending the full PRD and full plan every time, you can send Codex only:

```text
Use prd.md and plan.md as project reference.
Now implement Task 4 from task.md.
Only modify the files listed in that task.
```

This gives the AI a smaller working context.

The AI does not need to rethink the whole product every time.

It only needs to solve the current task.

### Important Note

`task.md` does not magically reduce tokens by itself.

It helps when you use it like this:

```text
Give Codex one task at a time.
Keep the task small.
Mention the relevant files.
Mention acceptance criteria.
Do not paste the whole PRD repeatedly.
```

That is how you reduce token/context overhead.

---

## 4. Task Execution Rules for Codex

Codex must follow these rules:

- Work on one task at a time.
- Do not skip ahead.
- Do not rewrite architecture unless the task says so.
- Do not put business logic in frontend components.
- Do not put backend business logic directly inside route handlers.
- Do not calculate financial totals in the frontend.
- Do not double-count transfers, wallet loads, or credit card payments.
- Do not send financial data to external AI APIs.
- Do not store PDF passwords.
- Do not add AI features before deterministic rules are implemented.
- Do not create one giant parser for all sources.
- Add tests for calculation-heavy backend logic.
- Keep modules isolated and replaceable.

---

## 5. Recommended Codex Prompt Pattern

Use this pattern for each implementation step:

```text
Read prd.md, plan.md, and task.md.

Implement Task <number>: <task name>.

Scope:
- Only modify files related to this task.
- Follow the architecture in plan.md.
- Keep business logic in backend services.
- Add or update tests where requested.
- Do not implement future tasks.

After implementation:
- Explain what changed.
- List files modified.
- Tell me how to run/test it.
```

---

# Phase 0: Repository Setup

## Task 0.1: Create Monorepo Structure

### Goal

Create the base project structure for frontend and backend.

### Files / Folders

```text
personal-finance-autopilot/
  backend/
  frontend/
  docs/
  docker-compose.yml
  README.md
```

### Acceptance Criteria

- Folder structure exists.
- README explains project purpose.
- Docs folder contains project documents.

---

## Task 0.2: Add Local Docker Compose

### Goal

Add local PostgreSQL for development.

### Files

```text
docker-compose.yml
.env.example
```

### Acceptance Criteria

- `docker compose up` starts PostgreSQL.
- `.env.example` documents required variables.

---

# Phase 1: Backend Foundation

## Task 1.1: Create FastAPI Backend Skeleton

### Files

```text
backend/app/main.py
backend/app/core/config.py
backend/app/core/database.py
backend/app/core/exceptions.py
backend/app/core/logging.py
backend/pyproject.toml
backend/README.md
```

### Acceptance Criteria

- `GET /health` returns healthy status.
- Backend starts without database errors if DB config exists.

---

## Task 1.2: Add SQLAlchemy and Alembic

### Acceptance Criteria

- Alembic can create migrations.
- Backend can connect to PostgreSQL.

---

## Task 1.3: Add Shared Enums and Utilities

### Required Enums

```text
TransactionType: income, expense, transfer
PaymentMethod: upi, wallet, credit_card, debit_card, bank_transfer, cash, unknown
SourceType: google_pay, phonepe, amazon_pay, paytm, onecard, credit_card, bank_statement, manual, other, generic_csv, generic_pdf
FinancialMode: salaried, freelancer, unemployed, student_dependent, custom
```

### Acceptance Criteria

- Enums are importable by other modules.
- Money helper safely handles Decimal values.
- Date helper normalizes common date formats.

---

# Phase 2: Authentication and Users

## Task 2.1: Create User Model

### Acceptance Criteria

- User table migration exists.
- User email is unique.
- User schema does not expose password hash.

---

## Task 2.2: Implement JWT Auth

### Endpoints

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Acceptance Criteria

- User can sign up.
- User can log in.
- Protected route returns current user.
- Passwords are hashed.
- JWT is required for protected APIs.

---

# Phase 3: Financial Profile and Runway Mode

## Task 3.1: Add Financial Profile Model

### Files

```text
backend/app/financial_profile/models.py
backend/app/financial_profile/schemas.py
backend/app/financial_profile/service.py
backend/app/financial_profile/router.py
```

### Fields

```text
id
user_id
financial_mode
available_balance
monthly_income_amount
monthly_income_day
expected_income_amount
expected_income_date
monthly_essential_expense_estimate
monthly_non_essential_expense_estimate
minimum_emergency_buffer
savings_goal_amount
credit_card_due_amount
credit_card_due_date
created_at
updated_at
```

### Acceptance Criteria

- Financial profile migration exists.
- Each user has at most one financial profile.
- Financial mode supports salaried, freelancer, unemployed, student_dependent, custom.

---

## Task 3.2: Add Financial Profile APIs

### Endpoints

```text
GET   /api/v1/financial-profile
PATCH /api/v1/financial-profile
```

### Acceptance Criteria

- User can fetch financial profile.
- User can update financial profile.
- One user cannot access another user's profile.
- Default profile is created if missing.

---

## Task 3.3: Add Financial Health Calculation Service

### Files

```text
backend/app/insights/financial_health.py
backend/tests/test_financial_health.py
```

### Required Calculations

For salaried:

```text
safe_to_spend =
available_balance
+ expected_income
- upcoming_bills
- credit_card_dues
- savings_goal
- emergency_buffer
```

For freelancer:

```text
safe_to_spend =
available_balance
+ confirmed_expected_income
- upcoming_bills
- credit_card_dues
- essential_expenses_until_next_income
- emergency_buffer
```

For unemployed:

```text
usable_balance = available_balance - emergency_buffer
runway_months = usable_balance / monthly_essential_expenses
recommended_daily_spend = usable_balance / desired_runway_days
```

For student/dependent:

```text
safe_to_spend =
available_balance
+ allowance_or_expected_income
- upcoming_bills
- emergency_buffer
- expected_essential_expenses
```

### Acceptance Criteria

- Negative safe-to-spend returns zero.
- Unemployed mode returns runway.
- Handles missing income without crashing.
- Returns explanation string.
- Unit tests cover all financial modes.

---

# Phase 4: Frontend Foundation

## Task 4.1: Create Next.js Frontend

### Acceptance Criteria

- Frontend starts locally.
- Home page renders.
- Tailwind works.

---

## Task 4.2: Add Auth Pages

### Pages

```text
/login
/signup
```

### Acceptance Criteria

- User can sign up from frontend.
- User can log in from frontend.
- Authenticated API requests include token.

---

## Task 4.3: Add App Layout

### Pages

```text
/dashboard
/import
/transactions
/subscriptions
/bills
/alerts
/settings
```

### Acceptance Criteria

- Protected pages require login.
- Navigation works.

---

## Task 4.4: Add Financial Profile Settings UI

### Page

```text
/settings
```

### Fields

```text
financial_mode
available_balance
monthly_income_amount
monthly_income_day
expected_income_amount
expected_income_date
monthly_essential_expense_estimate
minimum_emergency_buffer
savings_goal_amount
credit_card_due_amount
credit_card_due_date
```

### Acceptance Criteria

- User can view current financial profile.
- User can update financial profile.
- Form shows mode-specific helper text.
- Unemployed mode explains runway calculation.

---

# Phase 5: Import System

## Task 5.1: Create Import Models

### Tables

```text
transaction_sources
uploads
```

### Acceptance Criteria

- Upload metadata can be stored.
- Source type is stored.
- Upload status supports pending, previewed, processed, failed.

---

## Task 5.2: Create Parser Interface and Registry

### Files

```text
backend/app/parsers/base.py
backend/app/parsers/registry.py
```

### Acceptance Criteria

- New parsers can be registered without changing import flow.
- Parser returns normalized transactions.

---

## Task 5.3: Add Generic CSV Parser

### Acceptance Criteria

- Parser works on sample CSV.
- Parser returns normalized ParsedTransaction list.
- Invalid rows do not crash parser.

---

## Task 5.4: Add Generic PDF Parser

### Requirements

- Use text-based extraction first.
- Use pdfplumber or PyMuPDF.
- Detect transaction-like rows.
- Support password field during parsing.
- Do not store or log PDF password.
- If no text found, return clear error saying OCR may be needed.

### Acceptance Criteria

- Text-based PDF can be parsed.
- Password-protected PDF error is handled clearly.
- Image-based PDF does not crash.
- Parser returns preview rows.

---

## Task 5.5: Add Import Upload and Preview API

### Endpoints

```text
POST /api/v1/import/upload
POST /api/v1/import/uploads/{upload_id}/preview
GET  /api/v1/import/uploads
```

### Acceptance Criteria

- User can upload PDF, CSV, or Excel.
- User can preview transactions.
- Failed rows are shown.

---

## Task 5.6: Add Confirm Import API

### Endpoint

```text
POST /api/v1/import/uploads/{upload_id}/confirm
```

### Acceptance Criteria

- Confirmed rows become transactions.
- Duplicate rows are not double-counted.
- Upload status updates to processed.

---

# Phase 6: Transactions

## Task 6.1: Create Transaction Model and APIs

### Endpoints

```text
GET    /api/v1/transactions
GET    /api/v1/transactions/{transaction_id}
PATCH  /api/v1/transactions/{transaction_id}
DELETE /api/v1/transactions/{transaction_id}
```

### Acceptance Criteria

- User can list transactions.
- User can filter by month, category, source, payment method.
- User can edit category and merchant.
- User cannot access another user's transactions.

---

## Task 6.2: Add Transfer and Credit Card Payment Detection

### Acceptance Criteria

- Transfers are excluded from expense totals.
- Credit card merchant transactions count as expenses.
- Credit card bill payment does not count as expense again.

---

# Phase 7: Categorization

## Task 7.1: Add Default Categories

### Acceptance Criteria

- Default categories exist for every user or globally.
- Categories can be used by transactions.

---

## Task 7.2: Add Rule-Based Categorization

### Acceptance Criteria

- Common merchants are categorized.
- Unknown merchants go to Other.
- User category rules override default rules.

---

## Task 7.3: Add User Category Correction Rules

### Acceptance Criteria

- Editing transaction category creates/updates user rule.
- Future imports use user rule first.

---

# Phase 8: Deduplication and Enrichment

## Task 8.1: Add Fingerprint Deduplication

### Acceptance Criteria

- Exact duplicates are detected.
- Duplicate transactions are not double-counted.

---

## Task 8.2: Add Fuzzy Deduplication

### Acceptance Criteria

- Same payment from Google Pay and bank statement can be detected as likely duplicate.
- Duplicate relation is stored.

---

## Task 8.3: Add Transaction Detail Enrichment

### Acceptance Criteria

- Richer merchant/display name is kept.
- Raw descriptions are preserved.
- Enrichment does not change amount incorrectly.

---

# Phase 9: Dashboard and Insights

## Task 9.1: Add Dashboard API

### Endpoint

```text
GET /api/v1/dashboard?month=YYYY-MM
```

### Response Includes

```text
summary
category_breakdown
source_breakdown
payment_method_breakdown
largest_expenses
upcoming_bills
subscriptions
alerts
primary_insight
safe_to_spend
runway_months
monthly_burn_rate
recommended_daily_spend
calculation_explanation
```

### Acceptance Criteria

- Dashboard excludes transfers from expenses.
- Dashboard uses financial profile.
- Unemployed users get runway as primary insight.
- Salaried users get safe-to-spend as primary insight.

---

## Task 9.2: Add Dashboard UI

### Acceptance Criteria

- Dashboard does not show misleading safe-to-spend for unemployed users.
- Dashboard displays calculation explanation.
- Dashboard handles empty data.

---

## Task 9.3: Add Overspending Detection

### Acceptance Criteria

- Category overspending alert is generated.
- Daily burn rate warning is generated.
- Alerts explain reason.

---

## Task 9.4: Add Unusual Spending Detection

### Acceptance Criteria

- Large unusual transaction is flagged.
- New merchant high spend is flagged.
- User can mark as normal.

---

# Phase 10: Subscriptions and Bills

## Task 10.1: Add Subscription Model and Detection

### Acceptance Criteria

- Recurring payments are detected.
- Same merchant + similar amount + repeated interval creates subscription candidate.
- User can confirm or reject.

---

## Task 10.2: Add Bills CRUD

### Acceptance Criteria

- User can add/edit/delete bills.
- Upcoming bills are shown on dashboard.
- Bills affect safe-to-spend and runway calculations.

---

## Task 10.3: Add Credit Card Due Tracking

### Acceptance Criteria

- User can enter due date and due amount.
- Credit card due affects safe-to-spend.
- Credit card payment is not double-counted as spending.

---

# Phase 11: Source-Specific Parsers

## Task 11.1: Add Google Pay Parser

### Acceptance Criteria

- Parses Google Pay PDF/text export where available.
- Normalizes merchant, amount, date, payment method.
- Includes parser tests.

---

## Task 11.2: Add PhonePe Parser

### Acceptance Criteria

- Parses PhonePe PDF/text export where available.
- Normalizes merchant, amount, date, payment method.
- Includes parser tests.

---

## Task 11.3: Add Amazon Pay Parser

### Acceptance Criteria

- Parses Amazon Pay PDF/text export where available.
- Normalizes merchant, amount, date, payment method.
- Includes parser tests.

---

## Task 11.4: Add OneCard / Credit Card Parser

### Acceptance Criteria

- Parses card statement PDF.
- Separates card purchases from card bill payments.
- Includes parser tests.

---

# Phase 12: Alerts, Polish, and Deployment

## Task 12.1: Add Alert APIs and UI

### Acceptance Criteria

- Alerts are shown on dashboard and alerts page.
- User can dismiss alerts.
- Duplicate alerts are avoided.

---

## Task 12.2: Add Demo Data

### Demo Data Includes

- Salaried user
- Unemployed user
- Google Pay transactions
- PhonePe transactions
- Amazon Pay transactions
- OneCard transactions
- Bank fallback transactions
- Duplicate transactions
- Subscriptions
- Bills
- Unusual spending

### Acceptance Criteria

- Demo account clearly shows the app's intelligence.
- Runway mode can be demonstrated.

---

## Task 12.3: Add Tests and Quality Checks

### Acceptance Criteria

- Backend tests pass.
- Frontend builds.
- No obvious financial calculation errors.

---

## Task 12.4: Deploy MVP

### Recommended Deployment

```text
Frontend: Vercel
Backend: Render/Railway
Database: Supabase/Neon PostgreSQL
```

### Acceptance Criteria

- Public frontend URL works.
- Backend API works.
- Database migrations applied.
- Demo user works.

---

# 13. Current Priority

The immediate next tasks should be:

```text
Task 3.1: Add Financial Profile Model
Task 3.2: Add Financial Profile APIs
Task 3.3: Add Financial Health Calculation Service
Task 4.4: Add Financial Profile Settings UI
Task 9.1: Update Dashboard API with primary insight
Task 9.2: Update Dashboard UI
```

This fixes the biggest current product weakness:

```text
The app should not assume no income means no money.
```

For unemployed users, the app should show runway.

For salaried users, the app should show safe-to-spend.

For freelancers, the app should show cashflow safety.
