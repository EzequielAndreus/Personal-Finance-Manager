from flask import Blueprint, render_template, session
from datetime import datetime
from sqlalchemy import func
from models import db, Expense
from utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Main dashboard with statistics"""
    user_id = session.get("user_id")

    total_expenses = (
        db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar()
        or 0
    )
    total_debts = (
        db.session.query(func.sum(Expense.amount))
        .filter(Expense.user_id == user_id, Expense.due_date.isnot(None))
        .scalar()
        or 0
    )

    expenses_count = Expense.query.filter_by(user_id=user_id).count()
    debts_count = Expense.query.filter(
        Expense.user_id == user_id, Expense.due_date.isnot(None)
    ).count()

    recent_expenses = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.created_at.desc())
        .limit(5)
        .all()
    )

    upcoming_debts = (
        Expense.query.filter(
            Expense.user_id == user_id,
            Expense.due_date.isnot(None),
            Expense.due_date >= datetime.utcnow().date(),
        )
        .order_by(Expense.due_date.asc())
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        total_expenses=total_expenses,
        total_debts=total_debts,
        expenses_count=expenses_count,
        debts_count=debts_count,
        recent_expenses=recent_expenses,
        upcoming_debts=upcoming_debts,
    )
