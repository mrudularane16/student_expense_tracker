from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from utils import category_breakdown, get_period, month_options

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("/")
@login_required
def index():
    period = get_period(request.args.get("month"), default="current")
    return render_template(
        "categories.html",
        breakdown=category_breakdown(current_user.id, period),
        period=period,
        months=month_options(current_user.id, period),
        endpoint="categories.index",
        picker_extra={},
    )