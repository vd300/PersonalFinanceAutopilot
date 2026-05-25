export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type BreakdownItem = {
  name: string;
  amount: number;
};

export type FinancialMode = "salaried" | "freelancer" | "unemployed" | "student_dependent" | "custom";

export type FinancialProfile = {
  id: string;
  user_id: string;
  financial_mode: FinancialMode;
  available_balance: number | string;
  monthly_income_amount: number | string | null;
  monthly_income_day: number | null;
  expected_income_amount: number | string | null;
  expected_income_date: string | null;
  monthly_essential_expense_estimate: number | string;
  monthly_non_essential_expense_estimate: number | string | null;
  minimum_emergency_buffer: number | string;
  savings_goal_amount: number | string;
  credit_card_due_amount: number | string | null;
  credit_card_due_date: string | null;
  created_at: string;
  updated_at: string;
};

export type PrimaryInsight = {
  type: "safe_to_spend" | "runway" | "cashflow_safety" | "allowance_remaining";
  title: string;
  value: number | null;
  message: string;
};

export type Dashboard = {
  month: string;
  summary: {
    income: number;
    expenses: number;
    net_savings: number;
    transfers: number;
    transaction_count: number;
    average_daily_spend: number;
    credit_card_due: number;
  };
  category_breakdown: BreakdownItem[];
  source_breakdown: BreakdownItem[];
  payment_method_breakdown: BreakdownItem[];
  largest_expenses: Array<{ id: string; date: string; merchant: string; amount: number; category: string }>;
  upcoming_bills: Array<{ id: string; name: string; expected_amount: number; next_due_date: string; is_auto_detected: boolean }>;
  subscriptions: Array<{ id: string; merchant_name: string; amount: number; frequency: string; next_expected_payment_date: string; status: string; confidence_score: number }>;
  alerts: Array<{ id: string; title: string; message: string; severity: string }>;
  financial_mode: FinancialMode;
  primary_insight: PrimaryInsight;
  safe_to_spend: number | null;
  runway_months: number | null;
  monthly_burn_rate: number;
  recommended_daily_spend: number | null;
  emergency_buffer_status: "protected" | "at_risk" | "depleted";
  calculation_explanation: string;
  cashflow_projection: {
    projected_expenses: number;
    projected_savings: number;
    average_daily_spend: number;
    remaining_days: number;
    confidence: string;
    explanation: string;
  };
};

export type Transaction = {
  id: string;
  transaction_date: string;
  raw_description: string;
  merchant_name: string | null;
  display_name: string | null;
  amount: number;
  transaction_type: string;
  payment_method: string;
  source_type: string;
  category: string | null;
  is_unusual: boolean;
  is_duplicate: boolean;
  duplicate_of_transaction_id: string | null;
};
