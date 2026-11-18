from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import Transaction
from utils import (
    get_totals,
    category_breakdown,
    get_period,
    month_options,
    monthly_summary,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    period = get_period(request.args.get("month"), default="current")

    recent_query = Transaction.query.filter_by(user_id=current_user.id)
    if period["start"]:
        recent_query = recent_query.filter(
            Transaction.date >= period["start"], Transaction.date < period["end"]
        )
    recent = recent_query.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(5).all()

    full_breakdown = category_breakdown(current_user.id, period)

    chart_data = {
        "category": {
            "labels": [c["name"] for c in full_breakdown],
            "values": [float(c["total"]) for c in full_breakdown],
        },
        "monthly": monthly_summary(current_user.id, months=6),
    }

    return render_template(
        "dashboard.html",
        totals=get_totals(current_user.id, period),
        breakdown=full_breakdown[:5],
        recent=recent,
        chart_data=chart_data,
        period=period,
        months=month_options(current_user.id, period),
        endpoint="dashboard.index",
        picker_extra={},
    )