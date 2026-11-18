from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_

from extensions import db
from models import Transaction, Category
from utils import get_period, month_options

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

MAX_AMOUNT = Decimal("9999999999.99")  # fits Numeric(12, 2)
PER_PAGE = 10
SORT_COLUMNS = {
    "date": Transaction.date,
    "amount": Transaction.amount,
    "category": Category.name,
}


def validate(form):
    """Check the submitted form. Returns (values, cleaned_data, error)."""
    values = {
        "type": form.get("type", ""),
        "amount": form.get("amount", "").strip(),
        "category_id": form.get("category_id", ""),
        "date": form.get("date", ""),
        "description": form.get("description", "").strip(),
    }

    if values["type"] not in ("income", "expense"):
        return values, None, "Please choose income or expense."

    try:
        amount = Decimal(values["amount"].replace(",", "")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return values, None, "Enter a valid amount."
    if amount <= 0:
        return values, None, "Amount must be greater than zero."
    if amount > MAX_AMOUNT:
        return values, None, "That amount is too large."

    try:
        txn_date = date.fromisoformat(values["date"])
    except ValueError:
        return values, None, "Please pick a valid date."

    category = None
    if values["type"] == "expense":
        cid = values["category_id"]
        category = db.session.get(Category, int(cid)) if cid.isdigit() else None
        if category is None:
            return values, None, "Please choose a category for the expense."

    if len(values["description"]) > 255:
        return values, None, "Note must be 255 characters or fewer."

    cleaned = {
        "type": values["type"],
        "amount": amount,
        "category_id": category.id if category else None,
        "date": txn_date,
        "description": values["description"],
    }
    return values, cleaned, None


def render_page(values=None, editing=None):
    """History (search, filter, month, sort, pages) on the left, add/edit form on the right."""
    q = request.args.get("q", "").strip()

    tx_type = request.args.get("type", "")
    if tx_type not in ("income", "expense"):
        tx_type = ""

    sort = request.args.get("sort", "date")
    if sort not in SORT_COLUMNS:
        sort = "date"

    direction = request.args.get("dir", "desc")
    if direction not in ("asc", "desc"):
        direction = "desc"

    page = max(request.args.get("page", 1, type=int), 1)
    period = get_period(request.args.get("month"), default="all")

    # ----- build the query -----
    query = Transaction.query.filter_by(user_id=current_user.id).outerjoin(Category)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(like),
                Category.name.ilike(like),
                Transaction.type.ilike(like),
            )
        )
    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    if period["start"]:
        query = query.filter(Transaction.date >= period["start"], Transaction.date < period["end"])

    column = SORT_COLUMNS[sort]
    ordering = column.asc() if direction == "asc" else column.desc()
    query = query.order_by(ordering.nulls_last(), Transaction.id.desc())

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    if pagination.pages and page > pagination.pages:
        pagination = query.paginate(page=pagination.pages, per_page=PER_PAGE, error_out=False)

    # ----- URL parameters shared by every link on the page (page number is left out) -----
    args = {
        "q": q or None,
        "type": tx_type or None,
        "sort": sort if sort != "date" else None,
        "dir": direction if direction != "desc" else None,
        "month": None if period["key"] == "all" else period["key"],
    }
    picker_extra = {k: v for k, v in args.items() if v is not None and k != "month"}
    search_hidden = {k: v for k, v in args.items() if v is not None and k != "q"}

    def sort_header(col):
        if sort == col:
            new_dir = "asc" if direction == "desc" else "desc"
        else:
            new_dir = "asc" if col == "category" else "desc"
        arrow = ""
        if sort == col:
            arrow = "▲" if direction == "asc" else "▼"
        return {
            "url": url_for("transactions.index", **dict(args, sort=col, dir=new_dir)),
            "active": sort == col,
            "arrow": arrow,
        }

    if values is None:
        values = {
            "type": "expense",
            "amount": "",
            "category_id": "",
            "date": date.today().isoformat(),
            "description": "",
        }

    return render_template(
        "transactions.html",
        pagination=pagination,
        transactions=pagination.items,
        categories=Category.query.order_by(Category.name).all(),
        q=q,
        tx_type=tx_type,
        args=args,
        search_hidden=search_hidden,
        picker_extra=picker_extra,
        sort_links={c: sort_header(c) for c in SORT_COLUMNS},
        period=period,
        months=month_options(current_user.id, period),
        endpoint="transactions.index",
        values=values,
        editing=editing,
    )


@transactions_bp.route("/")
@login_required
def index():
    return render_page()


@transactions_bp.route("/add", methods=["POST"])
@login_required
def add():
    values, data, error = validate(request.form)
    if error:
        flash(error, "error")
        return render_page(values=values)

    db.session.add(Transaction(user_id=current_user.id, **data))
    db.session.commit()
    flash("Transaction added.", "success")
    return redirect(url_for("transactions.index"))


@transactions_bp.route("/<int:txn_id>/edit", methods=["GET", "POST"])
@login_required
def edit(txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        values, data, error = validate(request.form)
        if error:
            flash(error, "error")
            return render_page(values=values, editing=txn)
        for key, value in data.items():
            setattr(txn, key, value)
        db.session.commit()
        flash("Transaction updated.", "success")
        return redirect(url_for("transactions.index"))

    values = {
        "type": txn.type,
        "amount": f"{txn.amount:.2f}",
        "category_id": txn.category_id or "",
        "date": txn.date.isoformat(),
        "description": txn.description or "",
    }
    return render_page(values=values, editing=txn)


@transactions_bp.route("/<int:txn_id>/delete", methods=["POST"])
@login_required
def delete(txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first_or_404()
    db.session.delete(txn)
    db.session.commit()
    flash("Transaction deleted.", "success")
    return redirect(url_for("transactions.index"))