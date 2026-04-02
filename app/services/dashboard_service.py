from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import cast, extract, func, Integer
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord
from app.schemas.dashboard import CategoryTotal, MonthlyTrend, SummaryResponse


def _last_n_month_keys(n: int) -> list[str]:
    today = date.today()
    year = today.year
    month = today.month
    keys: list[str] = []
    for _ in range(n):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(keys))


def get_dashboard_summary(db: Session) -> SummaryResponse:
    totals = (
        db.query(FinancialRecord.type, func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .filter(FinancialRecord.is_deleted.is_(False))
        .group_by(FinancialRecord.type)
        .all()
    )
    total_income = sum(total for record_type, total in totals if record_type == "income")
    total_expenses = sum(total for record_type, total in totals if record_type == "expense")

    categories = (
        db.query(FinancialRecord.category, func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .filter(FinancialRecord.is_deleted.is_(False))
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )

    recent_activity_count = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.is_deleted.is_(False))
        .filter(FinancialRecord.record_date >= (date.today() - timedelta(days=7)))
        .count()
    )

    year_expr = cast(extract("year", FinancialRecord.record_date), Integer)
    month_expr = cast(extract("month", FinancialRecord.record_date), Integer)
    monthly_raw = (
        db.query(
            year_expr.label("year"),
            month_expr.label("month"),
            FinancialRecord.type,
            func.coalesce(func.sum(FinancialRecord.amount), 0.0).label("total"),
        )
        .filter(FinancialRecord.is_deleted.is_(False))
        .group_by(year_expr, month_expr, FinancialRecord.type)
        .order_by(year_expr, month_expr)
        .all()
    )

    trend_map: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for year, month, record_type, total in monthly_raw:
        month_key = f"{int(year):04d}-{int(month):02d}"
        trend_map[month_key][record_type] = float(total)

    rolling_months = _last_n_month_keys(6)
    monthly_trends = [
        MonthlyTrend(
            month=month,
            income=trend_map.get(month, {"income": 0.0, "expense": 0.0})["income"],
            expense=trend_map.get(month, {"income": 0.0, "expense": 0.0})["expense"],
        )
        for month in rolling_months
    ]

    return SummaryResponse(
        total_income=float(total_income),
        total_expenses=float(total_expenses),
        net_balance=float(total_income - total_expenses),
        category_totals=[CategoryTotal(category=cat, total=float(total)) for cat, total in categories],
        recent_activity_count=recent_activity_count,
        monthly_trends=monthly_trends,
    )
