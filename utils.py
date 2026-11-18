from datetime import date
from decimal import Decimal

from sqlalchemy import func

from extensions import db
from models import Transaction, Category


# ---------- Formatting ----------

def inr(value):
    """Format a number the Indian way: 1234567.5 -> 12,34,567.50 (drops .00)."""
    value = abs(Decimal(value or 0))
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


# ---------- Month filter ----------

def month_key(d):
    return f"{d.year}-{d.month:02d}"


def shift_month(d, delta):
    index = d.year * 12 + (d.month - 1) + delta
    return date(index // 12, index % 12 + 1, 1)


def get_period(raw, default="current"):
    """Turn the ?month= value into a period dict.

    raw can be None, "all", "current" or "YYYY-MM". An invalid value falls back
    to the default. start is inclusive and end is exclusive; both are None for
    "all time".
    """
    today_month = date.today().replace(day=1)
    if raw is None:
        raw = default

    start = None
    if raw == "current":
        start = today_month
    elif raw != "all":
        try:
            year, month = raw.split("-")
            start = date(int(year), int(month), 1)
        except (ValueError, TypeError):
            start = today_month if default == "current" else None

    if start is None:
        return {"key": "all", "start": None, "end": None,
                "label": "All time", "prev": None, "next": None}

    following = shift_month(start, 1)
    return {
        "key": month_key(start),
        "start": start,
        "end": following,
        "label": start.strftime("%B %Y"),
        "prev": month_key(shift_month(start, -1)),
        "next": month_key(following) if following <= today_month else None,
    }


def month_options(user_id, period):
    """Months for the dropdown: every month with data, the current one, the selected one."""
    rows = (
        db.session.query(
            func.extract("year", Transaction.date),
            func.extract("month", Transaction.date),
        )
        .filter(Transaction.user_id == user_id)
        .distinct()
        .all()
    )
    months = {date(int(y), int(m), 1) for y, m in rows}
    months.add(date.today().replace(day=1))
    if period["start"]:
        months.add(period["start"])
    return [{"key": month_key(d), "label": d.strftime("%B %Y")}
            for d in sorted(months, reverse=True)]


# ---------- Totals ----------

def _sum(user_id, kind, start=None, end=None):
    query = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id, Transaction.type == kind
    )
    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date < end)
    return Decimal(query.scalar())


def get_totals(user_id, period=None):
    """Income and expense for the period; balance is always all-time."""
    start = period["start"] if period else None
    end = period["end"] if period else None
    return {
        "income": _sum(user_id, "income", start, end),
        "expense": _sum(user_id, "expense", start, end),
        "balance": _sum(user_id, "income") - _sum(user_id, "expense"),
    }


def category_breakdown(user_id, period=None):
    """Expense totals per category for the period, biggest first."""
    query = (
        db.session.query(Category.name, func.sum(Transaction.amount), func.count(Transaction.id))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user_id, Transaction.type == "expense")
    )
    if period and period["start"]:
        query = query.filter(Transaction.date >= period["start"], Transaction.date < period["end"])

    rows = (
        query.group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    top = rows[0][1] if rows else 0
    grand_total = sum(r[1] for r in rows) if rows else 0
    return [
        {
            "name": name,
            "total": total,
            "count": count,
            "percent": int(total / top * 100) if top else 0,
            "share": round(total / grand_total * 100) if grand_total else 0,
        }
        for name, total, count in rows
    ]
def monthly_summary(user_id, months=6):
    """Income, expense and end-of-month balance for the last N months (oldest first)."""
    this_month = date.today().replace(day=1)
    first = shift_month(this_month, -(months - 1))

    year = func.extract("year", Transaction.date)
    month = func.extract("month", Transaction.date)
    rows = (
        db.session.query(year, month, Transaction.type, func.sum(Transaction.amount))
        .filter(Transaction.user_id == user_id, Transaction.date >= first)
        .group_by(year, month, Transaction.type)
        .all()
    )

    sums = {}
    for y, m, kind, total in rows:
        sums[(int(y), int(m), kind)] = Decimal(total)

    # Balance carried in from before the first month shown
    running = _sum(user_id, "income", end=first) - _sum(user_id, "expense", end=first)

    labels, income, expense, balance = [], [], [], []
    for i in range(months):
        d = shift_month(first, i)
        inc = sums.get((d.year, d.month, "income"), Decimal(0))
        exp = sums.get((d.year, d.month, "expense"), Decimal(0))
        running += inc - exp
        labels.append(d.strftime("%b %Y"))
        income.append(float(inc))
        expense.append(float(exp))
        balance.append(float(running))

    return {"labels": labels, "income": income, "expense": expense, "balance": balance}