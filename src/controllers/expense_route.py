from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from sqlalchemy import func
from models import db, Expense
from utils.decorators import login_required

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/expenses/new", methods=["GET", "POST"])
@login_required
def new_expense():
    """Create a new expense"""
    if request.method == "POST":
        try:
            name = request.form.get("name")
            amount = request.form.get("amount")
            category = request.form.get("category")
            date_str = request.form.get("date")
            due_date_str = request.form.get("due_date")
            element = request.form.get("element")
            comment = request.form.get("comment")

            if not name or not amount or not category or not date_str:
                flash("Please fill in all required fields", "warning")
                return redirect(url_for("expenses.new_expense"))

            expense = Expense(
                name=name,
                amount=float(amount),
                category=category,
                date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                element=element if element else None,
                comment=comment if comment else None,
                user_id=session.get("user_id"),
            )

            if due_date_str:
                expense.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            db.session.add(expense)
            db.session.commit()
            flash("Expense created successfully!", "success")
            return redirect(url_for("dashboard.index"))

        except ValueError:
            db.session.rollback()
            flash("Invalid data format. Please check your inputs.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating expense: {str(e)}", "danger")

    return render_template(
        "new_expense.html", today=datetime.now().strftime("%Y-%m-%d")
    )


@expense_bp.route("/expenses")
@login_required
def expenses_list():
    """List all expenses"""
    user_id = session.get("user_id")
    expenses = (
        Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    )

    total = sum(e.amount for e in expenses)

    return render_template("expenses.html", expenses=expenses, total=total)


@expense_bp.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    """Edit an existing expense"""
    expense = Expense.query.get_or_404(id)

    if expense.user_id != session.get("user_id"):
        flash("You don't have permission to edit this expense", "danger")
        return redirect(url_for("expenses.expenses_list"))

    if request.method == "POST":
        try:
            expense.name = request.form.get("name")
            expense.amount = float(request.form.get("amount"))
            expense.category = request.form.get("category")
            expense.date = datetime.strptime(
                request.form.get("date"), "%Y-%m-%d"
            ).date()
            expense.element = request.form.get("element")
            expense.comment = request.form.get("comment")

            due_date_str = request.form.get("due_date")
            expense.due_date = (
                datetime.strptime(due_date_str, "%Y-%m-%d").date()
                if due_date_str
                else None
            )

            db.session.commit()
            flash("Expense updated successfully!", "success")
            return redirect(url_for("expenses.expenses_list"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating expense: {str(e)}", "danger")

    return render_template("edit_expense.html", expense=expense)


@expense_bp.route("/expenses/<int:id>/delete", methods=["POST"])
@login_required
def delete_expense(id):
    """Delete an expense"""
    expense = Expense.query.get_or_404(id)

    if expense.user_id != session.get("user_id"):
        flash("You don't have permission to delete this expense", "danger")
        return redirect(url_for("expenses.expenses_list"))

    try:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting expense: {str(e)}", "danger")

    return redirect(url_for("expenses.expenses_list"))


@expense_bp.route("/debts")
@login_required
def debts_list():
    """List all debts (expenses with a due date)"""
    user_id = session.get("user_id")
    debts = (
        Expense.query.filter(Expense.user_id == user_id, Expense.due_date.isnot(None))
        .order_by(Expense.due_date.asc())
        .all()
    )

    total_debts = sum(d.amount for d in debts)
    overdue_debts = [d for d in debts if d.is_overdue]
    total_overdue = sum(d.amount for d in overdue_debts)

    return render_template(
        "debts.html",
        debts=debts,
        total_debts=total_debts,
        overdue_count=len(overdue_debts),
        total_overdue=total_overdue,
    )


@expense_bp.route("/summary")
@login_required
def summary():
    """General summary of expenses and debts"""
    user_id = session.get("user_id")

    all_expenses = (
        Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    )

    debts = [e for e in all_expenses if e.is_debt]
    paid_expenses = [e for e in all_expenses if not e.is_debt]

    categories_data = (
        db.session.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        )
        .filter_by(user_id=user_id)
        .group_by(Expense.category)
        .all()
    )

    monthly_data = (
        db.session.query(
            func.to_char(func.date_trunc('month', Expense.date), 'YYYY-MM').label('month'),
            func.sum(Expense.amount).label('total'),
        )
        .filter_by(user_id=user_id)
        .group_by("month")
        .order_by("month")
        .all()
    )

    total_paid = sum(e.amount for e in paid_expenses)
    total_debts = sum(d.amount for d in debts)
    grand_total = total_paid + total_debts

    return render_template(
        "summary.html",
        paid_expenses=paid_expenses,
        debts=debts,
        categories=categories_data,
        monthly_data=monthly_data,
        total_paid=total_paid,
        total_debts=total_debts,
        grand_total=grand_total,
    )
