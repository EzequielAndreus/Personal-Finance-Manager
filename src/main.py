import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost/postgres",
)
# Example: username=postgres, password=password, host=localhost, dbname=postgres
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------
# Database Models
# ---------------------------


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    element = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Expense {self.name} - ${self.amount}>"


class Debt(db.Model):
    __tablename__ = "debts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    element = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Debt {self.name} - ${self.amount}>"


# ---------------------------
# Entry Point
# ---------------------------


def main():
    print("Hello from Milestone 1!")


if __name__ == "__main__":
    main()
