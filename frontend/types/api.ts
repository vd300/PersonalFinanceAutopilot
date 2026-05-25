export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type BreakdownItem = {
  name: string;
  amount: number;
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
  safe_to_spend: {
    amount: number;
    available_basis: string;
    deductions: Record<string, number>;
    explanation: string;
  };
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

