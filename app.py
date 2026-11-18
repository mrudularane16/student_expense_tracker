from flask import Flask, flash, redirect, request, url_for
from flask_wtf.csrf import CSRFError
from sqlalchemy import inspect

from config import Config
from extensions import db, login_manager, migrate, csrf
from models import Category
from utils import inr

EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
]


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    app.jinja_env.filters["inr"] = inr

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.transactions import transactions_bp
    from routes.categories import categories_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Your session expired or the form was invalid. Please try again.", "error")
        return redirect(request.referrer or url_for("auth.signin"))

    # Seed the default categories once (only if the table already exists).
    with app.app_context():
        if inspect(db.engine).has_table("categories") and Category.query.count() == 0:
            db.session.add_all([Category(name=n) for n in EXPENSE_CATEGORIES])
            db.session.commit()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)