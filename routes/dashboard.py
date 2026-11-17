from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Transaction
from utils import get_totals, category_breakdown

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    recent = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        totals=get_totals(current_user.id),
        breakdown=category_breakdown(current_user.id)[:5],
        recent=recent,
    )