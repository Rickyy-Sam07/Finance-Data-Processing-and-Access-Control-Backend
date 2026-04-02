from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category: str
    total: float


class MonthlyTrend(BaseModel):
    month: str
    income: float
    expense: float


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    category_totals: list[CategoryTotal]
    recent_activity_count: int
    monthly_trends: list[MonthlyTrend]
