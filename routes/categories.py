from flask import Blueprint, render_template
from flask_login import login_required, current_user

from utils import category_breakdown

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("/")
@login_required
def index():
    return render_template("categories.html", breakdown=category_breakdown(current_user.id))