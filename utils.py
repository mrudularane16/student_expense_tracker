from decimal import Decimal, InvalidOperation

from sqlalchemy import func

from extensions import db
from models import Transaction, Category


def _as_decimal(value):
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def inr(value):
    """Format a number the Indian way: 1234567.5 -> 12,34,567.50 (drops .00)."""
    value = abs(_as_decimal(value))
    whole, dec = f"{value:.2f}".split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])
    return whole if dec == "00" else f"{whole}.{dec}"


def get_totals(user_id):
    """Total income, total expense and current balance for one user."""

    def total(kind):
        value = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(Transaction.user_id == user_id, Transaction.type == kind)
            .scalar()
        )
        return _as_decimal(value)

    income = total("income")
    expense = total("expense")
    return {"income": income, "expense": expense, "balance": income - expense}


def category_breakdown(user_id):
    """Expense totals per category, biggest first."""
    rows = (
        db.session.query(Category.name, func.sum(Transaction.amount), func.count(Transaction.id))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id, Transaction.type == "expense")
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    top = max((r[1] for r in rows), default=Decimal("0"))
    grand_total = sum((_as_decimal(r[1]) for r in rows), Decimal("0"))
    return [
        {
            "name": name,
            "total": _as_decimal(total),
            "count": count,
            "percent": int((_as_decimal(total) / top) * 100) if top else 0,
            "share": round((_as_decimal(total) / grand_total) * 100) if grand_total else 0,
        }
        for name, total, count in rows
    ]