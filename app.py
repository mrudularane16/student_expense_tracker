from flask import Flask

from config import Config
from extensions import db, login_manager
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
    login_manager.init_app(app)

    @app.template_filter("inr")
    def inr_filter(value):
        return inr(value)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.transactions import transactions_bp
    from routes.categories import categories_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)

    with app.app_context():
        db.create_all()
        if Category.query.count() == 0:
            db.session.add_all([Category(name=n) for n in EXPENSE_CATEGORIES])
            db.session.commit()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)