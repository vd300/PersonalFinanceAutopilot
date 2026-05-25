# PLAN: Personal Finance Autopilot

## 1. Purpose of This Plan

This document explains how to build the **Personal Finance Autopilot** app end to end in a way that is modular, maintainable, and easy to extend.

The main requirement is:

> New features, new transaction sources, new parsers, new categorization rules, new insights, and new dashboard widgets should be easy to add without changing the core infrastructure.

This plan is designed for use with Codex or another coding agent.

---

## 2. Product Direction

The product is a **multi-source personal finance aggregator**.

It should not rely only on bank statements.

The app should import transaction history from sources such as:

- Google Pay
- PhonePe
- Amazon Pay
- Paytm
- OneCard
- Credit card statements
- Bank statements
- Generic CSV/Excel files

The system should normalize all transactions into a common structure, deduplicate transactions across sources, enrich poor transaction descriptions, categorize expenses, detect subscriptions, detect unusual spending, and calculate safe-to-spend amount.

---

## 3. Recommended Architecture

Use a separated frontend and backend architecture.

```text
Frontend App
  ↓
FastAPI Backend
  ↓
PostgreSQL Database
  ↓
Background Jobs / Workers, optional
```

### Why This Architecture

This is better than putting everything inside a frontend framework because the app has serious backend logic:

- File parsing
- Transaction normalization
- Deduplication
- Categorization
- Subscription detection
- Safe-to-spend calculation
- Credit card handling
- Future AI features
- Future background jobs

FastAPI is a good fit because it is clean, Python-based, async-friendly, easy to test, and works well with data processing libraries.

---

## 4. Tech Stack

## 4.1 Backend

Use:

- **FastAPI** for backend API
- **PostgreSQL** for primary database
- **SQLAlchemy 2.0** for ORM
- **Alembic** for migrations
- **Pydantic v2** for request/response schemas
- **Pandas / openpyxl** for CSV and Excel parsing
- **pdfplumber / PyMuPDF** for text-based PDF transaction extraction
- **Tesseract OCR / cloud OCR later** only for scanned or image-based PDFs
- **RapidFuzz** for fuzzy matching and deduplication
- **APScheduler / Celery / RQ**, optional later for background jobs
- **Pytest** for backend tests

### Backend Deployment Options

Simple deployment options:

- Render
- Railway
- Fly.io
- DigitalOcean App Platform

Use managed PostgreSQL from:

- Supabase
- Neon
- Railway
- Render
- Aiven

For MVP, avoid AWS unless needed later.

---

## 4.2 Frontend

Use:

- **Next.js**
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**
- **React Query / TanStack Query**
- **Zod** for frontend validation
- **Recharts** for charts
- **React Hook Form** for forms

### Why Next.js

The frontend needs:

- Dashboard pages
- Upload flows
- Auth screens
- Settings screens
- Tables
- Charts
- Good developer experience
- Easy deployment

Next.js is appropriate because it gives a clean React app structure and deploys easily.

### Important Frontend Rule

The frontend should not contain business logic.

Frontend should only handle:

- UI rendering
- Form input
- Calling backend APIs
- Showing loading/error states
- Displaying data

All core financial logic should live in the FastAPI backend.

---

## 4.3 Auth

Recommended MVP options:

### Option A: Backend-owned auth

Use FastAPI with:

- Email/password login
- Password hashing with `passlib`
- JWT access tokens
- Refresh token support later

Pros:

- Full control
- Backend owns user identity
- No external dependency

Cons:

- More implementation work

### Option B: Supabase Auth

Use Supabase for auth and PostgreSQL.

Pros:

- Fast setup
- Handles auth flows
- Good for quick deployment

Cons:

- More external dependency
- Backend must verify Supabase JWTs

### Recommended Choice

For speed and simplicity:

> Use **Supabase Auth + PostgreSQL** if you want fastest deployment.

For learning and backend ownership:

> Use **FastAPI JWT Auth**.

This plan assumes **FastAPI JWT Auth** by default, but the auth layer should be isolated so it can be replaced later.

---

## 5. High-Level System Modules

The backend should be organized into modules.

```text
backend/
  app/
    main.py
    core/
    auth/
    users/
    imports/
    parsers/
    transactions/
    categorization/
    deduplication/
    enrichment/
    subscriptions/
    bills/
    alerts/
    insights/
    dashboard/
    settings/
    shared/
    tests/
```

Each module should own one business capability.

Do not put everything in one large file.

---

## 6. Backend Folder Structure

```text
backend/
  app/
    main.py

    core/
      config.py
      database.py
      security.py
      exceptions.py
      logging.py

    auth/
      router.py
      service.py
      schemas.py
      dependencies.py

    users/
      models.py
      router.py
      service.py
      schemas.py

    imports/
      models.py
      router.py
      service.py
      schemas.py
      validators.py

    parsers/
      base.py
      registry.py
      generic_csv.py
      bank_statement.py
      google_pay.py
      phonepe.py
      amazon_pay.py
      onecard.py
      credit_card.py

    transactions/
      models.py
      router.py
      service.py
      schemas.py
      repository.py

    categorization/
      service.py
      rules.py
      models.py
      schemas.py

    deduplication/
      service.py
      fingerprint.py
      fuzzy_matcher.py

    enrichment/
      service.py
      merchant_cleanup.py
      source_priority.py

    subscriptions/
      models.py
      router.py
      service.py
      detector.py
      schemas.py

    bills/
      models.py
      router.py
      service.py
      schemas.py

    alerts/
      models.py
      router.py
      service.py
      schemas.py

    insights/
      cashflow.py
      safe_to_spend.py
      overspending.py
      unusual_spending.py

    dashboard/
      router.py
      service.py
      schemas.py

    settings/
      models.py
      router.py
      service.py
      schemas.py

    shared/
      enums.py
      money.py
      dates.py
      pagination.py
      response.py

  alembic/
  tests/
  pyproject.toml
  README.md
```

---

## 7. Frontend Folder Structure

```text
frontend/
  app/
    layout.tsx
    page.tsx

    login/
      page.tsx

    signup/
      page.tsx

    dashboard/
      page.tsx

    import/
      page.tsx

    transactions/
      page.tsx

    subscriptions/
      page.tsx

    bills/
      page.tsx

    alerts/
      page.tsx

    settings/
      page.tsx

  components/
    ui/
    dashboard/
    import/
    transactions/
    subscriptions/
    bills/
    alerts/
    layout/

  lib/
    api.ts
    auth.ts
    format-money.ts
    format-date.ts
    constants.ts

  hooks/
    use-dashboard.ts
    use-transactions.ts
    use-imports.ts
    use-settings.ts

  types/
    api.ts
    transaction.ts
    dashboard.ts
    import.ts

  package.json
  next.config.ts
  tailwind.config.ts
```

---

## 8. Core Design Principles

## 8.1 Modular by Domain

Each major feature should live in its own module.

For example:

- Import logic should not know dashboard logic.
- Dashboard logic should not parse files.
- Categorization should not directly modify uploads.
- Deduplication should be reusable by every parser.

This makes it easier to add new features later.

---

## 8.2 Parser Plugin Architecture

Every transaction source should have its own parser.

All parsers should implement the same interface.

```python
class BaseTransactionParser:
    source_type: str

    def can_parse(self, file_metadata: dict) -> bool:
        pass

    def parse(self, file) -> list[ParsedTransaction]:
        pass
```

Example parser files:

```text
google_pay.py
phonepe.py
amazon_pay.py
onecard.py
bank_statement.py
generic_csv.py
```

Adding a new source later should only require:

1. Create a new parser file.
2. Register it in the parser registry.
3. Add source type to enum.
4. Add frontend option in import source dropdown.

No core import architecture should change.

---

## 8.3 Common Transaction Format

All sources must be normalized into one internal transaction format.

```text
ParsedTransaction
- transaction_date
- amount
- transaction_type
- payment_method
- source_type
- source_account_label
- raw_description
- description
- merchant_name
- display_name
- reference_id
- balance_after_transaction
- card_last_four
```

The rest of the system should only work with this common format.

This prevents every feature from needing to understand Google Pay, PhonePe, Amazon Pay, OneCard, etc.

---

## 8.4 Business Logic Belongs in Services

Routers should be thin.

A route should only:

- Validate request
- Call service
- Return response

Example:

```text
router.py → service.py → repository.py → database
```

Avoid putting business logic directly inside route handlers.

---

## 8.5 Replaceable Insight Engines

Insights should be implemented as isolated calculators.

Examples:

```text
safe_to_spend.py
cashflow.py
overspending.py
unusual_spending.py
subscription_detector.py
```

Each insight module should accept normalized transaction data and return a result.

This makes it easy to improve formulas later without changing APIs or database structure.

---

## 8.6 Avoid Double Counting

This is a critical principle.

The same expense can appear in multiple places:

- Google Pay transaction
- Bank debit transaction
- Credit card payment
- Credit card merchant transaction

The app must avoid double-counting.

Rules:

- UPI payment and bank debit for the same transaction should count once.
- Credit card merchant purchase should count as expense.
- Credit card bill payment should be treated as debt repayment or transfer, not a new expense.
- Wallet load should be transfer, not expense.
- Wallet merchant spend should be expense.

---

## 9. Data Flow

## 9.1 Import Flow

```text
User uploads file
  ↓
User selects source type
  ↓
Backend stores upload metadata
  ↓
Parser converts file into ParsedTransaction[]
  ↓
System validates parsed rows
  ↓
System normalizes fields
  ↓
System generates fingerprints
  ↓
System runs duplicate detection
  ↓
System enriches details using source priority
  ↓
System categorizes transactions
  ↓
System saves confirmed transactions
  ↓
System recalculates insights
  ↓
Dashboard updates
```

---

## 9.2 Dashboard Flow

```text
Frontend requests /api/dashboard?month=YYYY-MM
  ↓
Backend fetches transactions for user and month
  ↓
Backend excludes transfers from expense totals
  ↓
Backend calculates income, expenses, savings
  ↓
Backend calculates category breakdown
  ↓
Backend calculates source/payment method breakdown
  ↓
Backend fetches alerts, subscriptions, bills
  ↓
Backend calculates safe-to-spend
  ↓
Frontend renders dashboard cards and charts
```

---

## 10. Database Design Strategy

Use PostgreSQL.

Important database principles:

- Use UUID primary keys.
- Use timestamps on every table.
- Use soft delete where appropriate.
- Use indexes on common query fields.
- Keep raw imported data for debugging.
- Keep normalized transaction fields for app logic.
- Store source type for every transaction.
- Store transaction fingerprint for deduplication.
- Store user correction rules.

---

## 11. Core Tables

## 11.1 users

```text
id
name
email
password_hash
preferred_currency
monthly_income_day
savings_goal_amount
minimum_buffer_amount
created_at
updated_at
```

---

## 11.2 transaction_sources

```text
id
user_id
source_type
display_name
account_identifier
is_active
created_at
updated_at
```

---

## 11.3 uploads

```text
id
user_id
source_type
file_name
file_type
status
total_rows
imported_rows
duplicate_rows
failed_rows
error_message
created_at
updated_at
```

---

## 11.4 transactions

```text
id
user_id
upload_id
transaction_source_id
transaction_date
raw_description
description
merchant_name
display_name
amount
transaction_type
payment_method
source_type
source_account_label
category_id
balance_after_transaction
reference_id
card_last_four
is_recurring_candidate
is_unusual
is_duplicate
duplicate_of_transaction_id
user_notes
fingerprint
confidence_score
created_at
updated_at
deleted_at
```

---

## 11.5 categories

```text
id
user_id nullable
name
type
is_default
created_at
updated_at
```

---

## 11.6 user_category_rules

```text
id
user_id
keyword_or_merchant
category_id
created_from_transaction_id
created_at
updated_at
```

---

## 11.7 subscriptions

```text
id
user_id
merchant_name
amount
frequency
last_payment_date
next_expected_payment_date
category_id
status
confidence_score
source_type
created_at
updated_at
```

---

## 11.8 bills

```text
id
user_id
name
expected_amount
due_day
next_due_date
frequency
category_id
is_auto_detected
status
created_at
updated_at
```

---

## 11.9 alerts

```text
id
user_id
alert_type
title
message
severity
related_transaction_id
related_subscription_id
related_bill_id
status
created_at
updated_at
```

---

## 11.10 transaction_merge_links

```text
id
user_id
primary_transaction_id
duplicate_transaction_id
merge_reason
confidence_score
created_at
updated_at
```

---

## 12. API Design

Use REST APIs for MVP.

All endpoints should be versioned.

Base path:

```text
/api/v1
```

---

## 12.1 Auth APIs

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

---

## 12.2 Import APIs

```text
GET  /api/v1/import/sources
POST /api/v1/import/upload
POST /api/v1/import/uploads/{upload_id}/preview
POST /api/v1/import/uploads/{upload_id}/confirm
GET  /api/v1/import/uploads
GET  /api/v1/import/uploads/{upload_id}
DELETE /api/v1/import/uploads/{upload_id}
```

---

## 12.3 Parser APIs

Parser APIs are optional for direct exposure.

Prefer using parser services internally through import APIs.

If needed for debugging:

```text
POST /api/v1/parsers/preview
```

Request:

```json
{
  "source_type": "google_pay",
  "file_id": "..."
}
```

---

## 12.4 Transaction APIs

```text
GET    /api/v1/transactions
GET    /api/v1/transactions/{transaction_id}
PATCH  /api/v1/transactions/{transaction_id}
DELETE /api/v1/transactions/{transaction_id}
POST   /api/v1/transactions/{transaction_id}/mark-duplicate
POST   /api/v1/transactions/{transaction_id}/mark-transfer
POST   /api/v1/transactions/{transaction_id}/mark-normal
```

Transaction filters:

```text
month
category_id
source_type
payment_method
transaction_type
merchant
min_amount
max_amount
is_unusual
is_duplicate
```

---

## 12.5 Category APIs

```text
GET   /api/v1/categories
POST  /api/v1/categories
PATCH /api/v1/categories/{category_id}
DELETE /api/v1/categories/{category_id}
```

---

## 12.6 Dashboard APIs

```text
GET /api/v1/dashboard?month=YYYY-MM
```

Response should include:

```text
summary
category_breakdown
source_breakdown
payment_method_breakdown
upcoming_bills
subscriptions
alerts
safe_to_spend
cashflow_projection
```

---

## 12.7 Insight APIs

```text
GET /api/v1/insights/safe-to-spend
GET /api/v1/insights/cashflow?month=YYYY-MM
GET /api/v1/insights/overspending?month=YYYY-MM
GET /api/v1/insights/unusual-spending?month=YYYY-MM
```

These can be used by dashboard or future AI/chat features.

---

## 12.8 Subscription APIs

```text
GET   /api/v1/subscriptions
POST  /api/v1/subscriptions
PATCH /api/v1/subscriptions/{subscription_id}
DELETE /api/v1/subscriptions/{subscription_id}
POST  /api/v1/subscriptions/detect
```

---

## 12.9 Bill APIs

```text
GET   /api/v1/bills
POST  /api/v1/bills
PATCH /api/v1/bills/{bill_id}
DELETE /api/v1/bills/{bill_id}
```

---

## 12.10 Alert APIs

```text
GET   /api/v1/alerts
PATCH /api/v1/alerts/{alert_id}/dismiss
```

---

## 12.11 Settings APIs

```text
GET   /api/v1/settings
PATCH /api/v1/settings
```

---

## 13. Extension Strategy

The system should be built so future features can be added cleanly.

## 13.1 Adding a New Transaction Source

Example: adding CRED later.

Steps:

1. Add enum value: `cred`
2. Create parser: `parsers/cred.py`
3. Implement `BaseTransactionParser`
4. Register parser in `parsers/registry.py`
5. Add source option in frontend import dropdown
6. Add parser tests
7. Add demo sample file

No dashboard or insight logic should need to change.

---

## 13.2 Adding a New Insight

Example: “merchant price increase detection”.

Steps:

1. Create new file: `insights/merchant_price_increase.py`
2. Read normalized transactions
3. Return insight result
4. Add optional API route
5. Add dashboard widget if needed

No import or parser logic should change.

---

## 13.3 Adding AI Later

AI should be added as a separate module.

```text
ai/
  merchant_cleanup.py
  categorization.py
  monthly_summary.py
  chat.py
```

AI should consume normalized transaction data.

AI should not replace core deterministic calculations.

Recommended AI use cases later:

- Merchant cleanup
- Category suggestions
- Natural language monthly summaries
- Chat interface
- Import helper for messy copied text

---

## 13.4 Adding Background Jobs Later

For MVP, small CSV/Excel files can run synchronously.

PDF parsing can be slower and less predictable, so the import system should be designed to support background jobs later.

Later, add background jobs for:

- Large file parsing
- PDF parsing
- OCR processing for scanned PDFs
- Recalculating insights
- Subscription detection
- Alert generation
- AI summaries
- Email/SMS imports

Keep job logic in service functions so the same functions can be called synchronously or asynchronously.

---

## 14. Import and Parser Design

## 14.1 PDF-First Import Reality

Many payment apps and credit card apps export statements as PDF rather than CSV or Excel.

Therefore, PDF import should be treated as a first-class import path, not a future afterthought.

The system should support two PDF types:

### Text-Based PDFs

These PDFs contain selectable text.

Examples:

- Credit card statement PDF
- Some wallet/app transaction reports
- Bank-generated PDF statements

Use:

```text
pdfplumber
PyMuPDF
```

Approach:

1. Extract text and tables from PDF.
2. Detect transaction rows.
3. Normalize dates, amounts, merchant names, and descriptions.
4. Show parsed preview to the user.
5. Let the user correct columns or failed rows.

### Scanned/Image-Based PDFs

These PDFs are basically images.

Examples:

- Screenshot-generated PDF
- Some downloaded app statements
- Password-protected or flattened reports

Use OCR only when normal PDF text extraction fails.

MVP should not start with heavy OCR unless needed.

Recommended fallback flow:

```text
Try text extraction
  ↓
If no usable text found, mark PDF as image-based
  ↓
Ask user to upload CSV/Excel if available OR enable OCR processing
```

OCR can be added later using:

```text
Tesseract OCR
Google Document AI
AWS Textract
Azure Document Intelligence
```

For MVP, prefer local/open-source OCR only if it works reliably enough.

### PDF Password Handling

Many financial PDFs are password-protected.

The app should support an optional password field during upload.

Rules:

- Password should only be used during parsing.
- Do not store the PDF password.
- Show clear error if password is incorrect.
- Never log passwords.

### PDF Parser Design

PDF parsers should still follow the same parser interface.

Example parser modules:

```text
google_pay_pdf.py
phonepe_pdf.py
amazon_pay_pdf.py
onecard_pdf.py
credit_card_pdf.py
bank_statement_pdf.py
generic_pdf.py
```

PDF parsing should output the same common transaction format as CSV parsers.

This keeps the rest of the system unchanged.

---

## 14.2 Parser Interface

Each parser should return a list of parsed transactions and parsing warnings.

```python
class ParseResult(BaseModel):
    transactions: list[ParsedTransaction]
    warnings: list[str]
    failed_rows: list[FailedRow]
```

```python
class ParsedTransaction(BaseModel):
    transaction_date: date
    amount: Decimal
    transaction_type: TransactionType
    payment_method: PaymentMethod
    source_type: SourceType
    raw_description: str
    description: str | None = None
    merchant_name: str | None = None
    display_name: str | None = None
    reference_id: str | None = None
    balance_after_transaction: Decimal | None = None
    card_last_four: str | None = None
```

---

## 14.3 Parser Registry

Use a parser registry.

```python
PARSER_REGISTRY = {
    SourceType.GOOGLE_PAY: GooglePayParser(),
    SourceType.PHONEPE: PhonePeParser(),
    SourceType.AMAZON_PAY: AmazonPayParser(),
    SourceType.ONECARD: OneCardParser(),
    SourceType.BANK_STATEMENT: BankStatementParser(),
    SourceType.GENERIC_CSV: GenericCsvParser(),
}
```

The import service should call:

```python
parser = get_parser(source_type)
result = parser.parse(file)
```

---

## 14.4 Generic CSV and PDF Mapping

Many exports will not match expected columns.

The app should support column mapping.

Example:

```text
User maps:
Transaction Date → transaction_date
Narration → raw_description
Debit → amount
Credit → amount
Balance → balance_after_transaction
```

For PDFs, the user may need to review extracted rows because table extraction can be imperfect.

The UI should support:

- Preview extracted PDF rows
- Mark incorrect rows
- Edit extracted merchant/amount/date
- Confirm import only after review

Column mapping should be stored per user and source type later.

---

## 15. Deduplication Design

Deduplication is one of the most important parts of this app.

## 15.1 Exact Match

Exact duplicate if:

```text
same user
same date
same amount
same transaction type
same fingerprint
```

---

## 15.2 Fuzzy Match

Likely duplicate if:

```text
same user
amount difference <= ₹1
date difference <= 1 day
transaction type same
merchant similarity high OR reference id same OR UPI id same
```

Use RapidFuzz for merchant/description similarity.

---

## 15.3 Duplicate Handling

When duplicate is found:

- Do not count both in dashboard totals.
- Keep primary transaction as the richer record.
- Store duplicate relation in `transaction_merge_links`.
- Mark duplicate record as duplicate or skip saving it.
- Preserve raw data for audit/debugging.

---

## 15.4 Source Priority for Enrichment

Use this priority:

```text
user_edit
upi_wallet_app
amazon_pay
credit_card_app
bank_statement
generic_csv
```

A richer transaction should improve:

- display name
- merchant name
- category confidence
- description
- payment method
- reference ID

---

## 16. Categorization Design

Use rules first.

## 16.1 Default Rules

Create keyword rules for common merchants.

Examples:

```text
zomato, swiggy, restaurant, cafe → Food & Dining
bigbasket, blinkit, zepto, dmart → Groceries
uber, ola, rapido, metro → Transportation
netflix, spotify, prime, hotstar → Subscriptions
amazon, flipkart, myntra → Shopping
electricity, broadband, gas, mobile bill → Utilities
rent, landlord → Rent
```

---

## 16.2 User Correction Rules

When a user changes a category:

```text
merchant_name = Swiggy
new_category = Food & Dining
```

Create or update rule:

```text
Swiggy → Food & Dining
```

Future matching transactions should use this rule first.

---

## 16.3 Transfer Detection

Transfer detection is critical.

Mark as transfer if transaction looks like:

- Bank-to-bank transfer
- Wallet load
- Credit card payment
- Self transfer
- UPI to own account
- Refund reversal

Transfers should not count as expenses.

---

## 17. Insight Design

## 17.1 Safe-to-Spend

Formula:

```text
safe_to_spend =
available_balance
- upcoming_bills
- credit_card_dues
- savings_goal_remaining
- minimum_buffer
```

If balance is not available:

```text
safe_to_spend =
expected_income_remaining
- upcoming_bills
- credit_card_dues
- predicted_essential_expenses
- savings_goal_remaining
- minimum_buffer
```

Never show negative safe-to-spend.

```text
safe_to_spend = max(0, calculated_value)
```

Always explain the calculation.

---

## 17.2 Cashflow Prediction

Use current month activity and historical averages.

Inputs:

- Current income
- Current spending
- Remaining days in month
- Average daily spend
- Upcoming bills
- Subscriptions
- Credit card dues

Output:

- Projected expenses
- Projected savings
- Projected month-end balance, if balance exists
- Confidence level

---

## 17.3 Overspending Detection

Use simple deterministic rules.

Examples:

```text
current_category_spend > previous_3_month_average * 1.3
```

```text
current_daily_spend_rate > historical_daily_spend_rate * 1.25
```

---

## 17.4 Unusual Spending Detection

Flag transaction if:

```text
amount > category_average * 2
```

or

```text
new merchant + high amount
```

or

```text
credit card transaction much higher than usual
```

---

## 17.5 Subscription Detection

Detect recurring transactions by:

- Same merchant
- Similar amount
- Similar interval
- Repeated payments
- Subscription keywords

Frequency options:

```text
weekly
monthly
quarterly
yearly
unknown
```

---

## 18. Frontend Implementation Plan

## 18.1 Layout

Create an authenticated app layout with:

- Sidebar navigation
- Top bar
- User menu
- Mobile responsive layout

Navigation:

- Dashboard
- Import
- Transactions
- Subscriptions
- Bills
- Alerts
- Settings

---

## 18.2 Dashboard Page

Dashboard cards:

- Safe to spend
- Monthly income
- Monthly expenses
- Projected savings
- Upcoming bills
- Credit card dues
- Active alerts

Charts:

- Spending by category
- Spending by source
- Spending by payment method
- Monthly trend

---

## 18.3 Import Page

Flow:

1. Select source
2. Upload file
3. Preview parsed rows
4. Map columns if required
5. Review duplicate warnings
6. Confirm import
7. Show result summary

Important UX:

- Show source-specific instructions.
- Show accepted formats.
- Show sample CSV format.
- Show what data will be imported.
- Show privacy message.

---

## 18.4 Transactions Page

Features:

- Search transactions
- Filter by month
- Filter by category
- Filter by source
- Filter by payment method
- Edit category
- Edit merchant name
- Mark as transfer
- Mark as duplicate
- Delete transaction

Use a data table component.

---

## 18.5 Subscriptions Page

Show:

- Detected subscriptions
- Confirmed subscriptions
- Rejected subscriptions
- Amount
- Frequency
- Last payment date
- Next expected payment date
- Confidence score

---

## 18.6 Bills Page

Show:

- Upcoming bills
- Manual bills
- Auto-detected bills
- Credit card dues

Allow:

- Add bill
- Edit bill
- Delete bill

---

## 18.7 Settings Page

Allow user to configure:

- Currency
- Monthly income day
- Savings goal
- Minimum buffer
- Category budgets
- Credit card due dates
- Source labels

---

## 19. Testing Strategy

## 19.1 Backend Tests

Use Pytest.

Test:

- Auth
- File parsing
- Each parser
- Transaction normalization
- Deduplication
- Categorization
- Transfer detection
- Safe-to-spend calculation
- Cashflow prediction
- Subscription detection
- API permissions

---

## 19.2 Frontend Tests

Use:

- Playwright for end-to-end tests
- React Testing Library for component tests, optional

Test:

- Login
- Upload flow
- Dashboard loading
- Transaction filtering
- Category editing
- Bill creation
- Alert dismissal

---

## 19.3 Test Data

Create sample files for:

- Google Pay
- PhonePe
- Amazon Pay
- OneCard
- Generic bank statement
- Generic CSV

Include edge cases:

- Duplicate transaction across sources
- Refund
- Credit card payment
- Wallet load
- Subscription
- Unusual large transaction
- Missing merchant name
- Different date formats
- Failed rows

---

## 20. Deployment Plan

## 20.1 MVP Deployment

Recommended:

```text
Frontend: Vercel
Backend: Render or Railway
Database: Supabase or Neon PostgreSQL
```

---

## 20.2 Environment Variables

Backend:

```text
DATABASE_URL
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
CORS_ALLOWED_ORIGINS
ENVIRONMENT
```

Frontend:

```text
NEXT_PUBLIC_API_BASE_URL
```

---

## 20.3 CI/CD

Use GitHub Actions.

Backend pipeline:

```text
install dependencies
run lint
run tests
run migrations check
deploy
```

Frontend pipeline:

```text
install dependencies
run lint
run typecheck
build
deploy
```

---

## 21. Security Plan

## 21.1 User Data Isolation

Every query must filter by `user_id`.

Never trust frontend-provided user IDs.

Use authenticated user from JWT/session.

---

## 21.2 File Upload Security

Rules:

- Limit file size.
- Allow only supported file extensions.
- Validate MIME type.
- Do not execute uploaded files.
- Store files privately.
- Delete raw files after parsing if user chooses.

---

## 21.3 Privacy

For MVP:

- Do not send transaction data to external AI APIs.
- Do not sell or share data.
- Allow user to delete imports.
- Allow user to delete account later.

---

## 22. Development Phases

## Phase 0: Repo Setup

Deliverables:

- Monorepo structure
- Backend FastAPI app
- Frontend Next.js app
- Docker Compose for local PostgreSQL
- Environment config
- Basic README

---

## Phase 1: Backend Foundation

Deliverables:

- FastAPI app setup
- PostgreSQL connection
- SQLAlchemy models
- Alembic migrations
- Auth
- User model
- Default categories
- Health check API

---

## Phase 2: Frontend Foundation

Deliverables:

- Next.js app setup
- Tailwind
- shadcn/ui
- Auth pages
- Protected app layout
- API client
- Basic navigation

---

## Phase 3: Transaction Import MVP

Deliverables:

- Import source selection
- Upload API
- Generic CSV parser
- Generic PDF parser
- Bank statement parser
- PDF text extraction using pdfplumber or PyMuPDF
- Optional password input for protected PDFs
- Preview API
- Confirm import API
- Transaction storage
- Upload history

---

## Phase 4: Multi-Source Parsers

Deliverables:

- Google Pay parser
- Google Pay PDF parser
- PhonePe parser
- PhonePe PDF parser
- Amazon Pay parser
- Amazon Pay PDF parser
- OneCard / credit card parser
- OneCard / credit card PDF parser
- Parser registry
- Parser tests
- Sample CSV/Excel/PDF files

---

## Phase 5: Deduplication and Enrichment

Deliverables:

- Fingerprint generation
- Exact duplicate detection
- Fuzzy duplicate detection
- Source priority enrichment
- Duplicate review in UI
- Merge link records

---

## Phase 6: Categorization

Deliverables:

- Default category rules
- Merchant cleanup
- User category correction
- User category rules
- Transfer detection
- Credit card payment detection

---

## Phase 7: Dashboard

Deliverables:

- Dashboard API
- Income/expense summary
- Category breakdown
- Source breakdown
- Payment method breakdown
- Dashboard cards
- Dashboard charts

---

## Phase 8: Insights

Deliverables:

- Safe-to-spend calculation
- Cashflow projection
- Overspending detection
- Unusual spending detection
- Explainable insight responses

---

## Phase 9: Subscriptions and Bills

Deliverables:

- Subscription detector
- Subscription list UI
- Confirm/reject subscription
- Bills CRUD
- Upcoming bills
- Credit card due tracking

---

## Phase 10: Alerts

Deliverables:

- Alert generation
- Alert list API
- Alert display in dashboard
- Dismiss alert

---

## Phase 11: Polish

Deliverables:

- Empty states
- Loading states
- Error messages
- Responsive UI
- Demo mode
- Seed data
- Privacy messaging

---

## Phase 12: Deployment

Deliverables:

- Production environment variables
- Database migration setup
- Backend deployment
- Frontend deployment
- Public URL
- Smoke test checklist

---

## 23. Codex Execution Strategy

When using Codex, do not ask it to build everything at once.

Use small tasks.

Recommended order:

1. Create monorepo.
2. Create backend FastAPI skeleton.
3. Create database models.
4. Create migrations.
5. Create auth.
6. Create frontend skeleton.
7. Create import source selection UI.
8. Create generic CSV parser.
9. Create transaction storage.
10. Create dashboard API.
11. Create dashboard UI.
12. Add parsers one by one.
13. Add deduplication.
14. Add categorization.
15. Add insights.
16. Add subscriptions.
17. Add bills.
18. Add alerts.
19. Add tests.
20. Deploy.

---

## 24. Development Rules for Codex

Codex should follow these rules:

- Treat PDF import as a first-class requirement.
- Try text-based PDF extraction before OCR.
- Do not store PDF passwords.
- Do not put all backend logic in route files.
- Do not hardcode user IDs.
- Do not skip database migrations.
- Do not let frontend calculate financial totals.
- Do not double-count transfers.
- Do not send financial data to external AI APIs.
- Do not build AI features before deterministic rules.
- Do not create one massive parser for all sources.
- Do not create dashboard UI before backend data contracts are stable.
- Do not silently ignore failed import rows.
- Do not delete raw import information unless user chooses deletion.

---

## 25. Definition of Done

The app is ready when:

- User can sign up and log in.
- User can import at least two non-bank transaction sources.
- User can import a bank statement as fallback.
- Transactions are normalized into one schema.
- Duplicate transactions are detected.
- Transfers and credit card payments are not double-counted.
- Expenses are categorized automatically.
- User can manually correct categories.
- Dashboard shows useful monthly insights.
- Safe-to-spend is calculated and explained.
- Subscriptions are detected.
- Upcoming bills are shown.
- Alerts are generated.
- App has sample demo data.
- Backend tests pass.
- Frontend builds successfully.
- App is deployed publicly.

---

## 26. Future-Proofing Checklist

Before adding any new feature, ask:

1. Does this belong in backend or frontend?
2. Is this a new parser, new insight, new UI widget, or new data model?
3. Can this be added without modifying existing unrelated modules?
4. Does this affect transaction totals?
5. Could this cause double-counting?
6. Does this need a migration?
7. Does this need tests?
8. Does this expose private financial data?
9. Does this need background processing?
10. Should this be behind a feature flag?

---

## 27. Final Recommendation

Use this architecture:

```text
Next.js frontend
FastAPI backend
PostgreSQL database
Parser plugin system
Service-based backend modules
Deterministic rules first
AI later as optional layer
```

This gives the app a strong foundation.

It also makes future additions easier, such as:

- New payment apps
- New credit card providers
- SMS/email import
- AI summaries
- Mobile app
- Real-time integrations
- Advanced financial insights
