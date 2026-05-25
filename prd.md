# PRD: Personal Finance Autopilot

## 1. Product Name

**Personal Finance Autopilot**

A multi-source personal finance web app that helps users understand spending, track recurring bills/subscriptions, predict monthly cashflow, and calculate a practical “safe to spend” amount.

---

## 2. Problem Statement

Most people do not have a clear view of their money.

They struggle to understand:

- Where their money goes every month
- Which expenses are important vs unnecessary
- What bills are coming up
- Which subscriptions are silently charging them
- Whether they are overspending before it is too late
- How much money they can safely spend today

A major issue is that **bank statements alone do not explain spending clearly**.

Bank statements often show vague descriptions like:

```text
UPI/283828/PAYMENT/XYZBANK
POS DEBIT 9282
CARD TXN AMAZON PAY
```

These descriptions are not enough to understand what the expense was actually for.

However, apps like Google Pay, PhonePe, Amazon Pay, Paytm, and credit card apps like OneCard often have better transaction details, such as:

- Actual merchant name
- Payment notes
- Bill name
- Order context
- Recipient name
- Card transaction merchant
- Subscription or biller details

So the app should not rely only on bank statements. It should combine transactions from multiple sources to build a clearer financial picture.

---

## 3. Goal

Build an end-to-end personal finance app that imports transaction history from multiple sources and turns raw payment data into useful financial guidance.

The app should help users answer:

> “Where did my money actually go, and how much can I safely spend now?”

---

## 4. Target Users

### Primary Users

People who receive regular income and spend through multiple payment sources.

Examples:

- Salaried employees
- Freelancers
- Students managing monthly budgets
- Young professionals using UPI apps, wallets, credit cards, and e-commerce payments
- People with subscriptions, EMIs, rent, bills, and lifestyle spending

### User Skill Level

The app should be usable by non-technical users.

The user should not need to understand accounting, budgeting systems, or financial terminology.

---

## 5. Core Value Proposition

The app turns messy transactions from multiple apps into useful decisions.

Instead of only showing:

> “You spent ₹4,200.”

The app should say:

> “You spent ₹4,200 on food delivery this month across Swiggy and Zomato. This is 32% higher than usual. Based on your upcoming bills, you can safely spend ₹8,500 until your next salary.”

---

## 6. MVP Scope

The first version should focus on importing transactions from multiple real-world sources, not only bank statements.

Bank statements are useful, but they should be treated as a fallback source.

### Primary Import Sources

The MVP should support manual transaction import from:

- Google Pay
- PhonePe
- Amazon Pay
- Paytm, optional
- OneCard
- Credit card statements
- Bank CSV/Excel statements as fallback
- Generic CSV/Excel files

### Supported MVP Formats

Preferred formats:

- PDF statements
- CSV
- Excel
- Manually pasted transaction text, optional
- Screenshot/OCR support, later enhancement

Many payment apps and credit card apps usually export statements as PDF, so PDF import should be treated as a first-class MVP requirement.

For the first build, the app should support text-based PDF extraction first. OCR should be added only as a fallback for scanned/image-based PDFs.

### Source Priority

When the same transaction appears in multiple places, the system should prefer the source with richer transaction details.

Priority example:

1. User-corrected transaction details
2. UPI app or wallet transaction history
3. Amazon Pay transaction/order context
4. Credit card app or statement
5. Bank statement

### MVP Output

The app should provide:

- Multi-source transaction import
- Transaction deduplication across sources
- Transaction detail enrichment
- Better merchant identification
- Expense categorization
- Monthly spending summary
- Upcoming bill detection
- Subscription detection
- Credit card spend tracking
- Cashflow prediction
- Overspending warning
- Unusual spending detection
- Safe-to-spend amount
- Simple dashboard

---

## 7. Non-Goals for MVP

The MVP should not include:

- Direct bank account integration
- Real-time UPI sync
- Real-time bank sync
- Automatic scraping of payment apps
- Investment advice
- Tax filing
- Credit score tracking
- Stock or mutual fund recommendations
- Complex accounting features
- Native mobile app
- Multi-currency support
- AI chatbot as the main interface

These can be added later after the core product is working.

---

## 8. Main User Flow

### First-Time User Flow

1. User signs up or logs in.
2. User chooses an import source:
   - Google Pay
   - PhonePe
   - Amazon Pay
   - OneCard / credit card
   - Bank statement
   - Other wallet/payment app
3. User uploads or pastes transaction history.
4. System parses transactions based on the selected source.
5. System normalizes transactions into one common format.
6. System detects duplicate transactions across sources.
7. System keeps the best available transaction details.
8. System categorizes transactions automatically.
9. User reviews categorized transactions.
10. User optionally edits incorrect categories.
11. System generates dashboard insights.
12. User sees:
   - Total income
   - Total expenses
   - UPI/wallet/card spending breakdown
   - Category-wise spending
   - Upcoming bills
   - Credit card dues
   - Subscriptions
   - Safe-to-spend amount
   - Overspending alerts

### Returning User Flow

1. User logs in.
2. User uploads new transaction history from one or more sources.
3. System merges new transactions without duplicates.
4. System improves existing transactions if the new source has better details.
5. System updates insights.
6. User checks current month financial status.

---

## 9. Key Features

## 9.1 Multi-Source Transaction Import

### Description

User can import transaction history from multiple sources such as UPI apps, wallets, credit card apps, and bank statements.

This is a core feature because different sources contain different levels of detail.

Example:

- Bank statement may show: `UPI/29382/XYZBANK/TRANSFER`
- Google Pay may show: `Paid to Starbucks, Phoenix Mall, Coffee`
- Credit card statement may show: `AMAZON PAY INDIA PRIVATE LIMITED`
- Amazon Pay may show: `Order payment for headphones`

The app should combine these sources into one unified transaction database.

### Supported Sources for MVP

- Google Pay
- PhonePe
- Amazon Pay
- OneCard / credit card statements
- Bank CSV/Excel statements
- Other generic CSV/Excel files

### Requirements

The system should support source-specific parsing where possible.

Each imported transaction should be normalized into this common structure:

- Date
- Amount
- Direction: money out / money in
- Source app or account
- Payment method: UPI / wallet / credit card / debit card / bank transfer / cash / unknown
- Merchant or recipient
- Description
- Category
- Reference ID, if available
- Balance, if available
- Card/account identifier, if available

### User Story

As a user, I want to import transactions from Google Pay, PhonePe, Amazon Pay, OneCard, credit cards, and bank statements so the app can understand my real spending better than a bank statement alone.

### Acceptance Criteria

- User can select the transaction source before uploading.
- User can upload PDF, CSV, or Excel files for supported sources.
- System shows a preview of parsed transactions.
- User can map columns if column names are not recognized.
- System stores the original source for every transaction.
- Duplicate transactions across sources should not be imported twice.
- If duplicate transactions are found, the system should keep or merge the richer transaction details.
- Failed uploads should show a clear error message.

---

## 9.2 Transaction Detail Enrichment

### Description

The system should improve transaction quality by combining details from multiple sources.

For example, the same payment may appear in both a bank statement and Google Pay history. The bank description may be unclear, while Google Pay may show the actual merchant or note.

In that case, the app should use the Google Pay details for categorization and display.

### Detail Priority

When two records likely represent the same transaction, prefer details in this order:

1. User-edited merchant/category
2. UPI app or wallet transaction details
3. Amazon Pay order/payment context
4. Credit card app details
5. Bank statement description

### User Story

As a user, I want the app to combine transaction details from different apps so my spending history is understandable.

### Acceptance Criteria

- System can identify likely duplicate transactions across sources.
- System can merge transaction metadata without duplicating the expense amount.
- System should preserve the original raw descriptions.
- System should display the clearest merchant/recipient name.
- User can manually edit merchant name and category.

---

## 9.3 Transaction Categorization

### Description

System automatically assigns a category to each expense.

### Example Categories

- Food & Dining
- Groceries
- Rent
- Utilities
- Transportation
- Shopping
- Entertainment
- Subscriptions
- Healthcare
- Education
- Travel
- EMI / Loans
- Investments
- Salary / Income
- Credit Card Payment
- Wallet Transfer
- Bank Transfer
- Transfers
- Other

### Categorization Logic

MVP should use rule-based categorization first.

Examples:

- “Zomato”, “Swiggy”, “restaurant”, “cafe” → Food & Dining
- “Netflix”, “Spotify”, “Prime”, “Hotstar” → Subscriptions
- “Uber”, “Ola”, “Rapido”, “Metro” → Transportation
- “Amazon”, “Flipkart”, “Myntra” → Shopping
- “Rent”, “landlord” → Rent
- “Electricity”, “gas”, “broadband”, “wifi” → Utilities
- “OneCard payment”, “credit card payment” → Credit Card Payment
- “PhonePe wallet load”, “Amazon Pay balance” → Wallet Transfer

Later versions can add ML/AI categorization.

### Categorization Priority

Order of priority:

1. User-created merchant/category rule
2. Existing merchant match
3. Source-specific metadata
4. Default keyword rules
5. Recurring subscription mapping
6. Fallback to “Other”

### User Story

As a user, I want expenses categorized automatically so I do not have to manually classify every transaction.

### Acceptance Criteria

- Every imported transaction gets a category.
- User can manually edit a transaction category.
- Future similar transactions should use the user’s correction when possible.
- Uncategorized transactions should be marked as “Other”.
- Internal transfers and credit card payments should not be counted as expenses twice.

---

## 9.4 Monthly Spending Dashboard

### Description

User sees a simple dashboard for the selected month.

### Dashboard Metrics

- Total income
- Total expenses
- Net savings
- Spending by category
- Spending by source: Google Pay, PhonePe, Amazon Pay, credit card, bank
- Spending by payment method: UPI, wallet, credit card, debit card, bank transfer
- Largest expenses
- Number of transactions
- Average daily spend
- Current month burn rate
- Credit card outstanding estimate, if available

### User Story

As a user, I want a dashboard that clearly shows where my money went this month across all payment apps and cards.

### Acceptance Criteria

- User can select a month.
- Dashboard updates based on selected month.
- Expenses are grouped by category.
- Expenses can be filtered by source.
- Income and expenses are clearly separated.
- Transfers should not inflate expense totals.
- Dashboard should be readable on desktop and mobile browser.

---

## 9.5 Cashflow Prediction

### Description

System predicts how the user’s month may end based on current spending, income, upcoming recurring expenses, bills, and credit card dues.

### Basic Prediction Formula

```text
Projected End Balance = Current Balance + Expected Income - Expected Upcoming Expenses - Predicted Variable Spending
```

If balance is not available, use:

```text
Projected Monthly Savings = Monthly Income - Projected Monthly Expenses
```

### Prediction Inputs

- Current month income
- Current month spending so far
- Average daily spending
- Remaining days in month
- Known upcoming bills
- Detected subscriptions
- Credit card dues
- Historical monthly spending average

### User Story

As a user, I want to know whether I am likely to save money or run short by the end of the month.

### Acceptance Criteria

- System shows projected month-end balance or savings.
- System explains the calculation in simple language.
- Projection updates when new transactions are imported.
- System should not present predictions as guaranteed outcomes.

---

## 9.6 Overspending Warnings

### Description

System warns the user when spending is higher than usual or higher than budget.

### Warning Types

- Category overspending
- Overall monthly overspending
- Daily spend rate too high
- Unusual large transaction
- Low safe-to-spend amount
- Credit card usage too high
- Subscription cost increase

### Example Alerts

- “You have spent 80% of your food budget by the 15th of the month.”
- “Your shopping spend is 45% higher than your 3-month average.”
- “At this rate, you may overspend by ₹6,000 this month.”
- “Your credit card spending is already ₹18,000 this month.”

### User Story

As a user, I want early warnings before I overspend so I can control my expenses before the month ends.

### Acceptance Criteria

- System generates alerts based on transaction data.
- Alerts should be simple and actionable.
- User should not receive duplicate alerts for the same issue.
- User can dismiss alerts.

---

## 9.7 Unusual Spending Detection

### Description

System detects transactions or categories that are abnormal compared to the user’s usual behavior.

### Detection Logic

For MVP, use simple statistical rules.

Examples:

- A transaction is unusual if it is more than 2x the average transaction amount for that category.
- A category is unusual if current month spend is more than 30% above the previous 3-month average.
- A merchant is unusual if the user has never spent there before and the amount is high.
- A credit card transaction is unusual if it is much higher than the user’s usual card spend.

### User Story

As a user, I want the app to detect unusual spending so I can identify mistakes, fraud, or impulsive purchases.

### Acceptance Criteria

- System flags unusual transactions.
- System explains why the transaction was flagged.
- User can mark a flagged transaction as normal.
- Marking as normal should reduce repeated alerts for similar cases.

---

## 9.8 Subscription Detection

### Description

System detects recurring payments that look like subscriptions or bills.

### Detection Logic

A transaction may be a subscription if:

- Same or similar merchant appears repeatedly
- Amount is same or similar
- Transaction occurs monthly, weekly, quarterly, or yearly
- Merchant name matches known subscription keywords
- Source app identifies a biller/subscription

### Examples

- Netflix
- Spotify
- Amazon Prime
- Hotstar
- YouTube Premium
- Gym membership
- Cloud storage
- Internet bill
- Mobile bill
- Insurance premium

### User Story

As a user, I want to know which subscriptions I am paying for so I can cancel unnecessary ones.

### Acceptance Criteria

- System lists detected subscriptions.
- System shows amount, frequency, last payment date, and expected next payment date.
- User can confirm or reject a detected subscription.
- Confirmed subscriptions are used in cashflow prediction.

---

## 9.9 Upcoming Bills

### Description

System estimates upcoming bills based on recurring transactions.

### Examples

- Rent due on 5th
- Broadband due around 10th
- Credit card payment around 18th
- Insurance premium next month
- Mobile recharge due next week

### User Story

As a user, I want to know what bills are coming soon so I do not accidentally spend money needed for bills.

### Acceptance Criteria

- System shows upcoming bills for the next 30 days.
- Each bill includes expected amount and expected date.
- User can manually add, edit, or delete a bill.
- Upcoming bills affect safe-to-spend calculation.
- Credit card dues should be shown separately from normal subscriptions.

---

## 9.10 Safe-to-Spend Amount

### Description

The app calculates how much the user can safely spend without affecting upcoming bills, credit card payments, and savings goals.

### MVP Formula

```text
Safe to Spend = Current Available Balance - Upcoming Bills - Credit Card Dues - Minimum Buffer - Savings Goal
```

If balance is unavailable:

```text
Safe to Spend = Expected Income Remaining - Upcoming Bills - Credit Card Dues - Predicted Essential Expenses - Minimum Buffer - Savings Goal
```

### Required Inputs

- Current balance, if available
- Upcoming bills
- Credit card dues
- Expected income
- Essential expenses
- Savings goal
- Minimum buffer
- Remaining days in month

### Example Output

> “You can safely spend ₹7,800 until your next income date. This keeps ₹12,000 aside for rent, ₹3,000 for bills, ₹4,500 for credit card payment, and ₹5,000 as your emergency buffer.”

### User Story

As a user, I want to know how much money I can safely spend so I can make better daily spending decisions.

### Acceptance Criteria

- Safe-to-spend amount is visible on dashboard.
- System explains what was deducted.
- If data is insufficient, system asks user for missing values.
- Safe-to-spend should never be shown as a guarantee.
- Credit card expenses should not be double-counted when calculating available money.

---

## 10. User Settings

Users should be able to configure:

- Monthly income date
- Monthly savings goal
- Minimum balance buffer
- Monthly category budgets
- Preferred currency
- Important bills
- Credit card due dates
- Credit card billing cycle dates
- Transaction categories
- Import source labels

For MVP, preferred currency can default to INR.

---

## 11. AI Usage

AI should not be required for the first working version.

Recommended MVP approach:

1. Use source-specific parsers.
2. Use rules for transaction categorization.
3. Use heuristics for subscription detection.
4. Use fuzzy matching for duplicate detection.
5. Use simple statistical rules for unusual spending.
6. Add AI later for better merchant cleanup, natural language summaries, and smarter categorization.

### Optional AI Features for Later

- AI-generated monthly financial summary
- AI explanation of overspending patterns
- AI merchant name cleanup
- AI transaction categorization fallback
- AI chat interface: “Can I afford to spend ₹2,000 today?”
- AI import helper for messy pasted transaction text

---

## 12. Functional Requirements

### Authentication

- User can sign up.
- User can log in.
- User can log out.
- Each user only sees their own data.

### Multi-Source File Import

- User can choose import source.
- User can upload CSV/Excel transaction history.
- User can preview parsed transactions.
- User can confirm import.
- User can import from multiple sources into one account.
- System can deduplicate transactions across sources.
- System can enrich poor transaction descriptions using richer source data.

### Transactions

- User can view all transactions.
- User can filter transactions by month, category, merchant, payment method, and source.
- User can edit transaction category.
- User can edit merchant/display name.
- User can delete imported transactions.
- User can mark transactions as transfer, income, or expense.
- User can mark duplicate transactions.

### Dashboard

- User can see monthly income, expenses, and savings.
- User can see category-wise breakdown.
- User can see spending by source and payment method.
- User can see spending alerts.
- User can see safe-to-spend amount.

### Subscriptions

- User can view detected subscriptions.
- User can confirm/reject subscriptions.
- User can manually add subscriptions.

### Bills

- User can view upcoming bills.
- User can manually add/edit/delete bills.
- User can track credit card dues.

### Alerts

- User can see overspending alerts.
- User can see unusual transaction alerts.
- User can dismiss alerts.

---

## 13. Non-Functional Requirements

### Security

- User financial data must be private.
- Passwords must be hashed.
- Uploaded files should not be publicly accessible.
- Users must not access other users’ transactions.
- Raw uploaded files should be deletable.

### Privacy

- Do not sell or share user transaction data.
- Do not send transaction data to external AI APIs in MVP.
- If AI is added later, make it clear to users what data is sent.
- Allow users to delete their imported data.

### Performance

- Dashboard should load within 2 seconds for normal users.
- App should support at least 10,000 transactions per user.
- File upload should process 5,000 transactions without crashing.

### Reliability

- Duplicate import prevention is required.
- Failed import should not partially corrupt user data.
- Calculations should be deterministic and explainable.
- Internal transfers should not inflate spending totals.

---

## 14. Suggested Tech Stack

Use a stack that is easy to build and deploy.

### Recommended Stack

- Frontend: Next.js
- Backend: Next.js API routes
- Database: PostgreSQL
- ORM: Prisma
- Auth: Supabase Auth, Clerk, Auth.js, or custom auth
- File Parsing: Node CSV/XLSX parsers or Python service if needed
- Charts: Recharts
- Deployment: Vercel + Supabase, Render, Railway, or Fly.io

### Simple Deployment Option

Recommended for speed:

- Next.js full-stack app
- Supabase for Postgres and auth
- Vercel for frontend/backend deployment

This avoids AWS complexity.

---

## 15. Data Model

## 15.1 User

```text
User
- id
- name
- email
- password_hash or auth_provider_id
- preferred_currency
- monthly_income_day
- savings_goal_amount
- minimum_buffer_amount
- created_at
- updated_at
```

## 15.2 Transaction

```text
Transaction
- id
- user_id
- source_file_id
- transaction_date
- description
- raw_description
- merchant_name
- display_name
- amount
- transaction_type: income | expense | transfer
- payment_method: upi | wallet | credit_card | debit_card | bank_transfer | cash | unknown
- source_type: google_pay | phonepe | amazon_pay | paytm | onecard | credit_card | bank_statement | manual | other
- source_account_label
- category_id
- balance_after_transaction
- reference_id
- card_last_four nullable
- is_recurring_candidate
- is_unusual
- user_notes
- fingerprint
- confidence_score
- created_at
- updated_at
```

## 15.3 Category

```text
Category
- id
- user_id nullable
- name
- type: income | expense | transfer
- is_default
- created_at
- updated_at
```

## 15.4 Upload

```text
Upload
- id
- user_id
- file_name
- file_type
- source_type
- uploaded_at
- status: pending | processed | failed
- total_rows
- imported_rows
- duplicate_rows
- failed_rows
- error_message
```

## 15.5 Subscription

```text
Subscription
- id
- user_id
- merchant_name
- amount
- frequency: weekly | monthly | quarterly | yearly | unknown
- last_payment_date
- next_expected_payment_date
- category_id
- status: detected | confirmed | rejected | cancelled
- confidence_score
- source_type
- created_at
- updated_at
```

## 15.6 Bill

```text
Bill
- id
- user_id
- name
- expected_amount
- due_day
- next_due_date
- frequency
- category_id
- is_auto_detected
- status: active | inactive
- created_at
- updated_at
```

## 15.7 Alert

```text
Alert
- id
- user_id
- alert_type: overspending | unusual_transaction | upcoming_bill | low_safe_to_spend | subscription_detected | credit_card_due
- title
- message
- severity: low | medium | high
- related_transaction_id nullable
- related_subscription_id nullable
- related_bill_id nullable
- status: active | dismissed
- created_at
- updated_at
```

## 15.8 User Category Rule

```text
UserCategoryRule
- id
- user_id
- keyword_or_merchant
- category_id
- created_from_transaction_id
- created_at
```

## 15.9 Transaction Source

```text
TransactionSource
- id
- user_id
- source_type: google_pay | phonepe | amazon_pay | paytm | onecard | credit_card | bank_statement | manual | other
- display_name
- account_identifier nullable
- is_active
- created_at
- updated_at
```

## 15.10 Transaction Merge Link

```text
TransactionMergeLink
- id
- user_id
- primary_transaction_id
- duplicate_transaction_id
- merge_reason
- confidence_score
- created_at
```

---

## 16. Core Algorithms

## 16.1 Transaction Fingerprint and Deduplication

Used to avoid duplicate imports, especially when the same transaction appears in Google Pay, PhonePe, Amazon Pay, a credit card app, and a bank statement.

Basic fingerprint:

```text
fingerprint = hash(user_id + transaction_date + amount + transaction_type + normalized_merchant_or_description)
```

However, because descriptions can differ across sources, the system should also use fuzzy matching.

Possible duplicate if:

- Same user
- Same amount
- Same date or within 1 day
- Same direction: expense/income
- Similar merchant name, reference ID, or UPI ID
- Same card/account identifier, if available

When duplicates are detected:

- Do not count the amount twice.
- Keep both raw source records if needed.
- Use the richest source for display and categorization.

---

## 16.2 Source-Specific Parsing

Each source may have different columns and formats.

The app should support parser modules like:

```text
parseGooglePay()
parsePhonePe()
parseAmazonPay()
parseOneCard()
parseCreditCardStatement()
parseBankStatement()
parseGenericCsv()
```

Each parser should convert the source data into the common transaction format.

---

## 16.3 Merchant Cleanup

Convert messy transaction descriptions into cleaner merchant names.

Example:

```text
UPI-ZOMATO LIMITED-92839@paytm → Zomato
POS SWIGGY BANGALORE 1234 → Swiggy
AMAZON PAY INDIA PVT LTD → Amazon Pay
```

MVP can use keyword matching.

---

## 16.4 Categorization Algorithm

Order of priority:

1. User-created merchant/category rule
2. Existing merchant match
3. Source-specific metadata
4. Default keyword rules
5. Recurring subscription mapping
6. Fallback to “Other”

---

## 16.5 Subscription Detection Algorithm

Group transactions by cleaned merchant name.

For each merchant:

- Check if transactions repeat at similar intervals.
- Check if amounts are same or similar.
- Check if merchant appears at least 2 or 3 times.
- Assign confidence score.

Example:

```text
confidence_score = recurrence_score + amount_similarity_score + keyword_score
```

---

## 16.6 Overspending Detection Algorithm

For each category:

```text
current_month_category_spend > previous_3_month_average * 1.3
```

If true, create alert.

Also check:

```text
current_month_total_spend_rate > historical_daily_spend_rate * 1.25
```

---

## 16.7 Safe-to-Spend Algorithm

```text
safe_to_spend = available_balance - upcoming_bills - credit_card_dues - savings_goal_remaining - minimum_buffer
```

If result is negative:

```text
safe_to_spend = 0
```

The dashboard should explain the calculation.

---

## 17. Pages / Screens

## 17.1 Landing Page

Purpose: Explain the app and convert users to sign up.

Sections:

- Problem statement
- Key benefits
- How it works
- Supported sources
- Privacy-first message
- CTA: Upload transactions / Get started

## 17.2 Auth Pages

- Sign up
- Login
- Forgot password, optional

## 17.3 Dashboard

Main page after login.

Widgets:

- Safe-to-spend amount
- Income vs expenses
- Month-end projection
- Spending by category
- Spending by source
- Upcoming bills
- Credit card dues
- Active subscriptions
- Alerts

## 17.4 Import Transactions Page

Features:

- Choose source: Google Pay, PhonePe, Amazon Pay, OneCard, credit card, bank statement, or generic CSV
- Upload CSV/Excel/PDF where supported
- Preview parsed rows
- Map columns
- Show duplicate detection results
- Show enriched transaction details
- Confirm import
- Import result summary

## 17.5 Transactions Page

Features:

- Table of transactions
- Search
- Filters
- Edit category
- Edit merchant/display name
- Mark transfer/income/expense
- Mark duplicate
- Delete transaction

## 17.6 Subscriptions Page

Features:

- Detected subscriptions
- Confirm/reject subscription
- Next expected payment
- Monthly subscription total

## 17.7 Bills Page

Features:

- Upcoming bills
- Add/edit/delete manual bills
- Auto-detected bills
- Credit card dues

## 17.8 Settings Page

Features:

- Income day
- Savings goal
- Minimum buffer
- Category budgets
- Currency
- Credit card due dates
- Source labels

---

## 18. API Requirements

Example API endpoints:

```text
POST /api/import/upload
GET /api/import/uploads
POST /api/import/uploads/:id/preview
POST /api/import/uploads/:id/confirm

GET /api/import/sources
POST /api/import/sources

POST /api/parsers/google-pay
POST /api/parsers/phonepe
POST /api/parsers/amazon-pay
POST /api/parsers/onecard
POST /api/parsers/credit-card
POST /api/parsers/bank-statement
POST /api/parsers/generic-csv

GET /api/transactions
PATCH /api/transactions/:id
DELETE /api/transactions/:id
POST /api/transactions/:id/mark-duplicate
POST /api/transactions/:id/merge

GET /api/dashboard?month=YYYY-MM
GET /api/insights/cashflow?month=YYYY-MM
GET /api/insights/safe-to-spend

GET /api/subscriptions
PATCH /api/subscriptions/:id
POST /api/subscriptions
DELETE /api/subscriptions/:id

GET /api/bills
POST /api/bills
PATCH /api/bills/:id
DELETE /api/bills/:id

GET /api/alerts
PATCH /api/alerts/:id/dismiss

GET /api/settings
PATCH /api/settings
```

---

## 19. Success Metrics

The app is successful if users can:

- Upload transactions from multiple sources
- Understand their spending within 2 minutes
- See accurate category breakdowns
- Find recurring subscriptions
- See upcoming bills and credit card dues
- Get a useful safe-to-spend amount
- Receive meaningful overspending warnings

### Product Metrics

- Upload success rate
- Source parsing success rate
- Deduplication accuracy
- Categorization accuracy
- Number of transactions categorized automatically
- Number of subscriptions detected
- Number of alerts generated
- Number of user category corrections
- Weekly active users
- Returning users after first upload

---

## 20. MVP Build Phases

## Phase 1: Foundation

- Set up project
- Add authentication
- Add database schema
- Add protected dashboard shell
- Add default categories

## Phase 2: Multi-Source Transaction Import

- Add source selection
- Add PDF/CSV/Excel upload
- Add parsers for generic PDF, generic CSV, and bank statements
- Add parsers for Google Pay, PhonePe, Amazon Pay, and OneCard exports where possible
- Add text-based PDF extraction before OCR
- Add column mapping
- Parse transactions into common format
- Prevent duplicates
- Add fuzzy deduplication across sources
- Store original source metadata
- Enrich poor descriptions using richer source data

## Phase 3: Categorization

- Add default keyword rules
- Add merchant cleanup
- Add editable categories
- Save user correction rules
- Detect transfers and credit card payments

## Phase 4: Dashboard

- Monthly income/expense summary
- Category breakdown
- Source/payment method breakdown
- Transaction table
- Basic charts

## Phase 5: Insights

- Cashflow prediction
- Safe-to-spend calculation
- Overspending alerts
- Unusual spending detection

## Phase 6: Subscriptions, Bills, and Credit Cards

- Detect recurring payments
- Show subscriptions
- Predict next payment date
- Add upcoming bills page
- Add credit card due tracking

## Phase 7: Polish and Deployment

- Improve UI
- Add empty states
- Add loading states
- Add error handling
- Deploy to Vercel/Railway/Render
- Add seed/demo data

---

## 21. Demo Data Requirement

The app should include demo data so the project can be reviewed without uploading real transaction history.

Demo user should include:

- 4 months of transactions
- Google Pay transactions
- PhonePe transactions
- Amazon Pay transactions
- OneCard or credit card transactions
- Bank statement fallback transactions
- Salary income
- Rent
- Food delivery
- Groceries
- Subscriptions
- Shopping
- Transport
- Utilities
- Credit card payment
- At least one duplicate transaction across sources
- At least one unusual transaction
- At least one overspending alert
- At least three detected subscriptions

---

## 22. Important UX Principles

- Keep language simple.
- Do not shame the user for spending.
- Explain every financial insight.
- Show confidence level for detected subscriptions.
- Make manual corrections easy.
- Make duplicate handling transparent.
- Use practical labels like “safe”, “warning”, and “needs attention”.
- Avoid complex financial jargon.

---

## 23. Risk Areas

### Risk 1: Messy Export Formats

Different apps export transaction history differently.

Mitigation:

- Add source-specific parsers.
- Add generic CSV mapper.
- Show preview before import.
- Allow user correction.

### Risk 2: Duplicate Transactions

Same expense can appear in multiple sources.

Example:

- Google Pay shows UPI payment.
- Bank statement shows money debited for same payment.

Mitigation:

- Use fingerprinting and fuzzy matching.
- Do not count duplicate expenses twice.
- Keep the richer transaction detail for display.

### Risk 3: Incorrect Categorization

Rule-based categorization may be wrong.

Mitigation:

- Allow user edits.
- Save correction rules.
- Show “Other” instead of guessing aggressively.

### Risk 4: Privacy Concerns

Users may hesitate to upload financial data.

Mitigation:

- Explain privacy clearly.
- Avoid external AI APIs in MVP.
- Allow demo mode.
- Allow users to delete uploaded data.

### Risk 5: Wrong Financial Advice

The app should not act like a financial advisor.

Mitigation:

- Use language like “estimated”, “projected”, and “based on your data”.
- Avoid investment or tax advice.
- Explain calculations clearly.

---

## 24. Future Enhancements

- Direct bank integration
- UPI transaction sync
- Email bill detection
- SMS transaction import
- Gmail receipt import
- AI monthly report
- AI personal finance assistant
- WhatsApp or Telegram alerts
- Mobile app
- Shared household budgeting
- Goal-based planning
- Credit card due date tracking
- Subscription cancellation reminders
- Export to CSV/PDF
- Multi-currency support
- OCR for screenshots and PDFs

---

## 25. Definition of Done for MVP

The MVP is complete when:

- A user can sign up and log in.
- A user can choose an import source.
- A user can upload transactions from at least two non-bank sources such as Google Pay, PhonePe, Amazon Pay, OneCard, or a credit card statement.
- At least one supported non-bank source should work through PDF import.
- A user can also upload a bank PDF/CSV/Excel statement as fallback.
- Transactions are parsed and saved into one unified transaction database.
- Duplicate transactions across sources are detected and not double-counted.
- Richer source details are used to improve merchant names and categorization.
- Transactions are automatically categorized.
- User can correct categories.
- Dashboard shows monthly financial summary.
- App detects subscriptions.
- App shows upcoming bills and credit card dues.
- App calculates safe-to-spend amount.
- App shows overspending and unusual spending alerts.
- App has demo data.
- App is deployed and usable from a public URL.

---

## 26. Codex Build Instruction

Build this project as a production-quality MVP.

Prioritize:

1. Working end-to-end import flow
2. Multi-source transaction normalization
3. Reliable duplicate detection
4. Clean database schema
5. Explainable insights
6. Simple dashboard
7. Easy deployment

Avoid overengineering.

Do not start with AI-heavy features.

Build the rules-based and parser-based system first, then leave clean extension points for future AI features.
