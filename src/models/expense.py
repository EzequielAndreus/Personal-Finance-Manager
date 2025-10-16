from datetime import datetime
from . import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    element = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_debt(self):
        return self.due_date is not None

    @property
    def is_overdue(self):
        return self.due_date and self.due_date < datetime.utcnow().date()

    @property
    def days_until_due(self):
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow().date()
        return delta.days

    def __repr__(self):
        return f"<Expense {self.name} - ${self.amount}>"
