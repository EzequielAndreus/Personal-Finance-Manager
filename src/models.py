from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with expenses
    expenses = db.relationship(
        "Expense",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        """Sets the hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies whether the given password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)  # Null → not a debt
    element = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_debt(self):
        """Returns True if this expense is a debt (has a due date)."""
        return self.due_date is not None

    @property
    def is_overdue(self):
        """Returns True if the debt is overdue."""
        if not self.is_debt:
            return False
        return self.due_date < datetime.utcnow().date()

    @property
    def days_until_due(self):
        """Returns the number of days remaining until the due date (negative if overdue)."""
        if not self.is_debt:
            return None
        delta = self.due_date - datetime.utcnow().date()
        return delta.days

    def __repr__(self):
        return f"<Expense {self.name} - ${self.amount}>"
