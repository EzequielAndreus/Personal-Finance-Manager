from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from controllers.dashboard_route import dashboard_bp
from models import db
from models import User, Expense  # Import your database and models
from utils.db_init import init_db
import os


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:password@localhost/postgres",
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database
    db.init_app(app)

    # Import and register blueprints (routes)
    from controllers.auth_route import auth_bp
    from controllers.expense_route import expense_bp
    # from controllers.debt_route import debt_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(dashboard_bp)
    # app.register_blueprint(debt_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("500.html"), 500

    return app


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()  # Create tables if not exist
        init_db(app)

        # Seed predefined data if SEED_PREDEFINED is set
        if os.getenv("SEED_PREDEFINED", "0") in ("1", "true", "True"):
            from utils.db_init import seed_predefined_data
            seed_predefined_data(app)

    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)
