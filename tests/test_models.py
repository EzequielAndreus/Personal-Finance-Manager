import pytest
from datetime import datetime, date, timedelta
from models import User, Expense, db


class TestUser:
    """Test cases for User model"""

    @pytest.mark.unit
    def test_user_creation(self, db_session):
        """Test creating a new user"""
        user = User(username="testuser", is_admin=False)
        user.set_password("testpassword")
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.is_admin is False
        assert user.password_hash is not None
        assert user.created_at is not None

    @pytest.mark.unit
    def test_user_password_hashing(self, db_session):
        """Test password hashing and verification"""
        user = User(username="testuser")
        user.set_password("testpassword")
        
        # Password should be hashed
        assert user.password_hash != "testpassword"
        assert len(user.password_hash) > 0
        
        # Should verify correct password
        assert user.check_password("testpassword") is True
        
        # Should reject incorrect password
        assert user.check_password("wrongpassword") is False

    @pytest.mark.unit
    def test_user_repr(self, db_session):
        """Test user string representation"""
        user = User(username="testuser")
        assert repr(user) == "<User testuser>"

    @pytest.mark.unit
    def test_user_expenses_relationship(self, db_session):
        """Test user-expenses relationship"""
        user = User(username="testuser")
        user.set_password("testpassword")
        db_session.add(user)
        db_session.commit()

        # Create an expense for the user
        expense = Expense(
            name="Test Expense",
            amount=100.0,
            category="Food",
            date=date.today(),
            user_id=user.id
        )
        db_session.add(expense)
        db_session.commit()

        # Check relationship
        assert len(user.expenses) == 1
        assert user.expenses[0].name == "Test Expense"
        assert expense.user.username == "testuser"


class TestExpense:
    """Test cases for Expense model"""

    @pytest.mark.unit
    def test_expense_creation(self, db_session, sample_user):
        """Test creating a new expense"""
        expense = Expense(
            name="Test Expense",
            amount=150.75,
            category="Food",
            date=date.today(),
            user_id=sample_user.id,
            comment="Test comment"
        )
        db_session.add(expense)
        db_session.commit()

        assert expense.id is not None
        assert expense.name == "Test Expense"
        assert expense.amount == 150.75
        assert expense.category == "Food"
        assert expense.date == date.today()
        assert expense.user_id == sample_user.id
        assert expense.comment == "Test comment"
        assert expense.created_at is not None

    @pytest.mark.unit
    def test_expense_is_debt_property(self, db_session, sample_user):
        """Test is_debt property"""
        # Regular expense (no due_date)
        expense = Expense(
            name="Regular Expense",
            amount=100.0,
            category="Food",
            date=date.today(),
            user_id=sample_user.id
        )
        assert expense.is_debt is False

        # Debt (with due_date)
        debt = Expense(
            name="Debt",
            amount=200.0,
            category="Utilities",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            user_id=sample_user.id
        )
        assert debt.is_debt is True

    @pytest.mark.unit
    def test_expense_is_overdue_property(self, db_session, sample_user):
        """Test is_overdue property"""
        # Not a debt
        expense = Expense(
            name="Regular Expense",
            amount=100.0,
            category="Food",
            date=date.today(),
            user_id=sample_user.id
        )
        assert expense.is_overdue is None

        # Future debt
        future_debt = Expense(
            name="Future Debt",
            amount=200.0,
            category="Utilities",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            user_id=sample_user.id
        )
        assert future_debt.is_overdue is False

        # Overdue debt
        overdue_debt = Expense(
            name="Overdue Debt",
            amount=300.0,
            category="Utilities",
            date=date.today(),
            due_date=date.today() - timedelta(days=5),
            user_id=sample_user.id
        )
        assert overdue_debt.is_overdue is True

    @pytest.mark.unit
    def test_expense_days_until_due_property(self, db_session, sample_user):
        """Test days_until_due property"""
        # Not a debt
        expense = Expense(
            name="Regular Expense",
            amount=100.0,
            category="Food",
            date=date.today(),
            user_id=sample_user.id
        )
        assert expense.days_until_due is None

        # Future debt
        future_debt = Expense(
            name="Future Debt",
            amount=200.0,
            category="Utilities",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            user_id=sample_user.id
        )
        assert future_debt.days_until_due >= 29  # Allow for slight time differences

        # Overdue debt
        overdue_debt = Expense(
            name="Overdue Debt",
            amount=300.0,
            category="Utilities",
            date=date.today(),
            due_date=date.today() - timedelta(days=5),
            user_id=sample_user.id
        )
        assert overdue_debt.days_until_due <= -5  # Allow for slight time differences

    @pytest.mark.unit
    def test_expense_repr(self, db_session, sample_user):
        """Test expense string representation"""
        expense = Expense(
            name="Test Expense",
            amount=150.75,
            category="Food",
            date=date.today(),
            user_id=sample_user.id
        )
        assert repr(expense) == "<Expense Test Expense - $150.75>"

    @pytest.mark.unit
    def test_expense_optional_fields(self, db_session, sample_user):
        """Test expense with optional fields"""
        expense = Expense(
            name="Test Expense",
            amount=100.0,
            category="Food",
            date=date.today(),
            user_id=sample_user.id,
            element="Test Element",
            comment="Test Comment",
            due_date=date.today() + timedelta(days=7)
        )
        db_session.add(expense)
        db_session.commit()

        assert expense.element == "Test Element"
        assert expense.comment == "Test Comment"
        assert expense.due_date == date.today() + timedelta(days=7)
        assert expense.is_debt is True
