from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.shared.enums import FinancialMode


MONEY = Decimal("0.01")
MONTHS = Decimal("0.1")


@dataclass(frozen=True)
class FinancialHealthInput:
    financial_mode: FinancialMode | str
    available_balance: Decimal = Decimal("0")
    expected_income_amount: Decimal | None = None
    monthly_income_amount: Decimal | None = None
    upcoming_bills: Decimal = Decimal("0")
    credit_card_dues: Decimal = Decimal("0")
    savings_goal_amount: Decimal = Decimal("0")
    minimum_emergency_buffer: Decimal = Decimal("0")
    monthly_essential_expense_estimate: Decimal = Decimal("0")
    monthly_non_essential_expense_estimate: Decimal | None = None
    essential_expenses_until_next_income: Decimal | None = None
    desired_runway_days: int = 90


@dataclass(frozen=True)
class PrimaryInsight:
    type: str
    title: str
    value: Decimal | None
    message: str


@dataclass(frozen=True)
class FinancialHealthResult:
    financial_mode: FinancialMode
    primary_insight: PrimaryInsight
    safe_to_spend: Decimal | None
    runway_months: Decimal | None
    monthly_burn_rate: Decimal
    recommended_daily_spend: Decimal | None
    emergency_buffer_status: str
    calculation_explanation: str


def calculate_financial_health(payload: FinancialHealthInput) -> FinancialHealthResult:
    mode = FinancialMode(payload.financial_mode)
    available_balance = _money(payload.available_balance)
    upcoming_bills = _money(payload.upcoming_bills)
    credit_card_dues = _money(payload.credit_card_dues)
    savings_goal = _money(payload.savings_goal_amount)
    emergency_buffer = _money(payload.minimum_emergency_buffer)
    monthly_essential = _money(payload.monthly_essential_expense_estimate)
    monthly_non_essential = _money(payload.monthly_non_essential_expense_estimate)
    monthly_burn_rate = _money(monthly_essential + monthly_non_essential)

    if mode == FinancialMode.UNEMPLOYED:
        usable_balance = max(Decimal("0"), available_balance - emergency_buffer)
        runway_months = (
            _months(usable_balance / monthly_essential) if monthly_essential > 0 else None
        )
        daily_spend = (
            _money(usable_balance / Decimal(payload.desired_runway_days))
            if payload.desired_runway_days > 0
            else None
        )
        value = runway_months
        message = (
            f"Based on your current balance and essential monthly spending, your money may last "
            f"around {runway_months} months."
            if runway_months is not None
            else "Add an essential monthly expense estimate to calculate runway."
        )
        return FinancialHealthResult(
            financial_mode=mode,
            primary_insight=PrimaryInsight(
                type="runway",
                title="Financial runway",
                value=value,
                message=message,
            ),
            safe_to_spend=None,
            runway_months=runway_months,
            monthly_burn_rate=monthly_burn_rate,
            recommended_daily_spend=daily_spend,
            emergency_buffer_status=_emergency_buffer_status(available_balance, emergency_buffer),
            calculation_explanation=(
                "Runway uses available balance minus emergency buffer, divided by essential "
                "monthly expenses. Recommended daily spend spreads usable balance across the "
                "desired runway days."
            ),
        )

    if mode == FinancialMode.FREELANCER:
        confirmed_income = _money(payload.expected_income_amount)
        essential_until_income = _money(
            payload.essential_expenses_until_next_income
            if payload.essential_expenses_until_next_income is not None
            else monthly_essential
        )
        safe_to_spend = _clamped_money(
            available_balance
            + confirmed_income
            - upcoming_bills
            - credit_card_dues
            - essential_until_income
            - emergency_buffer
        )
        return _safe_to_spend_result(
            mode=mode,
            insight_type="cashflow_safety",
            title="Cashflow safety",
            safe_to_spend=safe_to_spend,
            monthly_burn_rate=monthly_burn_rate,
            emergency_buffer_status=_emergency_buffer_status(available_balance, emergency_buffer),
            explanation=(
                "Cashflow safety uses available balance plus confirmed expected income, then "
                "sets aside upcoming bills, credit card dues, essential expenses until next "
                "income, and emergency buffer."
            ),
        )

    if mode == FinancialMode.STUDENT_DEPENDENT:
        allowance_or_income = _money(
            payload.expected_income_amount or payload.monthly_income_amount
        )
        expected_essential = _money(
            payload.essential_expenses_until_next_income
            if payload.essential_expenses_until_next_income is not None
            else monthly_essential
        )
        safe_to_spend = _clamped_money(
            available_balance
            + allowance_or_income
            - upcoming_bills
            - emergency_buffer
            - expected_essential
        )
        return _safe_to_spend_result(
            mode=mode,
            insight_type="allowance_remaining",
            title="Allowance remaining",
            safe_to_spend=safe_to_spend,
            monthly_burn_rate=monthly_burn_rate,
            emergency_buffer_status=_emergency_buffer_status(available_balance, emergency_buffer),
            explanation=(
                "Allowance remaining uses available balance plus expected allowance or income, "
                "then sets aside upcoming bills, essential expenses, and emergency buffer."
            ),
        )

    income = _money(payload.expected_income_amount or payload.monthly_income_amount)
    essential_for_custom = monthly_essential if mode == FinancialMode.CUSTOM else Decimal("0")
    safe_to_spend = _clamped_money(
        available_balance
        + income
        - upcoming_bills
        - credit_card_dues
        - savings_goal
        - emergency_buffer
        - essential_for_custom
    )
    insight_type = "cashflow_safety" if mode == FinancialMode.CUSTOM else "safe_to_spend"
    title = "Cashflow safety" if mode == FinancialMode.CUSTOM else "Safe to spend"
    explanation = (
        "Safe to spend uses available balance plus expected income, then sets aside upcoming "
        "bills, credit card dues, savings goal, and emergency buffer."
    )
    if mode == FinancialMode.CUSTOM:
        explanation += " Custom mode also sets aside the essential monthly expense estimate."

    return _safe_to_spend_result(
        mode=mode,
        insight_type=insight_type,
        title=title,
        safe_to_spend=safe_to_spend,
        monthly_burn_rate=monthly_burn_rate,
        emergency_buffer_status=_emergency_buffer_status(available_balance, emergency_buffer),
        explanation=explanation,
    )


def _safe_to_spend_result(
    *,
    mode: FinancialMode,
    insight_type: str,
    title: str,
    safe_to_spend: Decimal,
    monthly_burn_rate: Decimal,
    emergency_buffer_status: str,
    explanation: str,
) -> FinancialHealthResult:
    return FinancialHealthResult(
        financial_mode=mode,
        primary_insight=PrimaryInsight(
            type=insight_type,
            title=title,
            value=safe_to_spend,
            message=f"Estimated {title.lower()} is {safe_to_spend}.",
        ),
        safe_to_spend=safe_to_spend,
        runway_months=None,
        monthly_burn_rate=monthly_burn_rate,
        recommended_daily_spend=None,
        emergency_buffer_status=emergency_buffer_status,
        calculation_explanation=explanation,
    )


def _money(value: Decimal | int | float | str | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


def _clamped_money(value: Decimal) -> Decimal:
    return max(Decimal("0.00"), _money(value))


def _months(value: Decimal) -> Decimal:
    return Decimal(value).quantize(MONTHS, rounding=ROUND_HALF_UP)


def _emergency_buffer_status(available_balance: Decimal, emergency_buffer: Decimal) -> str:
    if available_balance >= emergency_buffer:
        return "protected"
    if available_balance > 0:
        return "at_risk"
    return "depleted"
