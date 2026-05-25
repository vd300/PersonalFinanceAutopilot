from decimal import Decimal

from app.insights.financial_health import FinancialHealthInput, calculate_financial_health
from app.shared.enums import FinancialMode


def test_salaried_safe_to_spend_uses_expected_income_and_clamps_negative():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.SALARIED,
            available_balance=Decimal("1000"),
            expected_income_amount=Decimal("0"),
            upcoming_bills=Decimal("3000"),
            credit_card_dues=Decimal("2000"),
            savings_goal_amount=Decimal("1000"),
            minimum_emergency_buffer=Decimal("5000"),
        )
    )

    assert result.primary_insight.type == "safe_to_spend"
    assert result.safe_to_spend == Decimal("0.00")
    assert "upcoming bills" in result.calculation_explanation


def test_salaried_safe_to_spend_positive_amount():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.SALARIED,
            available_balance=Decimal("25000"),
            expected_income_amount=Decimal("50000"),
            upcoming_bills=Decimal("10000"),
            credit_card_dues=Decimal("7000"),
            savings_goal_amount=Decimal("15000"),
            minimum_emergency_buffer=Decimal("10000"),
        )
    )

    assert result.safe_to_spend == Decimal("33000.00")


def test_freelancer_uses_confirmed_income_and_essential_expenses_until_next_income():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.FREELANCER,
            available_balance=Decimal("30000"),
            expected_income_amount=Decimal("20000"),
            upcoming_bills=Decimal("8000"),
            credit_card_dues=Decimal("5000"),
            essential_expenses_until_next_income=Decimal("12000"),
            minimum_emergency_buffer=Decimal("10000"),
        )
    )

    assert result.primary_insight.type == "cashflow_safety"
    assert result.safe_to_spend == Decimal("15000.00")


def test_unemployed_returns_runway_and_daily_spend():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.UNEMPLOYED,
            available_balance=Decimal("85000"),
            monthly_essential_expense_estimate=Decimal("25000"),
            minimum_emergency_buffer=Decimal("10000"),
            desired_runway_days=75,
        )
    )

    assert result.primary_insight.type == "runway"
    assert result.safe_to_spend is None
    assert result.runway_months == Decimal("3.0")
    assert result.recommended_daily_spend == Decimal("1000.00")
    assert result.emergency_buffer_status == "protected"


def test_unemployed_handles_missing_expense_estimate_without_crashing():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.UNEMPLOYED,
            available_balance=Decimal("5000"),
            minimum_emergency_buffer=Decimal("10000"),
        )
    )

    assert result.runway_months is None
    assert result.recommended_daily_spend == Decimal("0.00")
    assert result.emergency_buffer_status == "at_risk"


def test_student_dependent_uses_allowance_or_expected_income():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.STUDENT_DEPENDENT,
            available_balance=Decimal("3000"),
            expected_income_amount=Decimal("12000"),
            upcoming_bills=Decimal("2000"),
            monthly_essential_expense_estimate=Decimal("6000"),
            minimum_emergency_buffer=Decimal("1000"),
        )
    )

    assert result.primary_insight.type == "allowance_remaining"
    assert result.safe_to_spend == Decimal("6000.00")


def test_custom_mode_is_conservative_and_returns_explanation():
    result = calculate_financial_health(
        FinancialHealthInput(
            financial_mode=FinancialMode.CUSTOM,
            available_balance=Decimal("20000"),
            expected_income_amount=Decimal("10000"),
            upcoming_bills=Decimal("5000"),
            credit_card_dues=Decimal("2000"),
            savings_goal_amount=Decimal("3000"),
            monthly_essential_expense_estimate=Decimal("7000"),
            minimum_emergency_buffer=Decimal("5000"),
        )
    )

    assert result.primary_insight.type == "cashflow_safety"
    assert result.safe_to_spend == Decimal("8000.00")
    assert "Custom mode" in result.calculation_explanation
