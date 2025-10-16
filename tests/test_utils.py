"""
Test utilities and helper functions
"""
import pytest
from datetime import date, timedelta
from models import User, Expense, db


class TestDataFactory:
    """Factory class for creating test data"""
    
    @staticmethod
    def create_user(username="testuser", is_admin=False, password="testpassword"):
        """Create a test user"""
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        return user
    
    @staticmethod
    def create_expense(user_id, name="Test Expense", amount=100.0, 
                      category="Food", expense_date=None, due_date=None, 
                      element=None, comment=None):
        """Create a test expense"""
        if expense_date is None:
            expense_date = date.today()
            
        expense = Expense(
            name=name,
            amount=amount,
            category=category,
            date=expense_date,
            user_id=user_id,
            element=element,
            comment=comment
        )
        
        if due_date:
            expense.due_date = due_date
            
        return expense
    
    @staticmethod
    def create_debt(user_id, name="Test Debt", amount=250.0, 
                   category="Utilities", days_until_due=30):
        """Create a test debt"""
        due_date = date.today() + timedelta(days=days_until_due)
        return TestDataFactory.create_expense(
            user_id=user_id,
            name=name,
            amount=amount,
            category=category,
            due_date=due_date
        )


class TestAssertions:
    """Custom assertions for testing"""
    
    @staticmethod
    def assert_expense_created(expense, expected_name, expected_amount, 
                              expected_category, expected_user_id):
        """Assert that an expense was created with correct attributes"""
        assert expense.id is not None
        assert expense.name == expected_name
        assert expense.amount == expected_amount
        assert expense.category == expected_category
        assert expense.user_id == expected_user_id
        assert expense.created_at is not None
    
    @staticmethod
    def assert_user_created(user, expected_username, expected_is_admin=False):
        """Assert that a user was created with correct attributes"""
        assert user.id is not None
        assert user.username == expected_username
        assert user.is_admin == expected_is_admin
        assert user.password_hash is not None
        assert user.created_at is not None


@pytest.fixture
def test_data_factory():
    """Provide test data factory"""
    return TestDataFactory


@pytest.fixture
def test_assertions():
    """Provide test assertions"""
    return TestAssertions


@pytest.fixture
def multiple_users(db_session):
    """Create multiple test users"""
    users = []
    for i in range(3):
        user = TestDataFactory.create_user(
            username=f"user{i+1}",
            is_admin=(i == 0)  # First user is admin
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    return users


@pytest.fixture
def multiple_expenses(db_session, multiple_users):
    """Create multiple test expenses for different users"""
    expenses = []
    categories = ["Food", "Transport", "Entertainment", "Utilities"]
    
    for i, user in enumerate(multiple_users):
        for j, category in enumerate(categories):
            expense = TestDataFactory.create_expense(
                user_id=user.id,
                name=f"{category} Expense {j+1}",
                amount=50.0 + (j * 25),
                category=category
            )
            db_session.add(expense)
            expenses.append(expense)
    
    db_session.commit()
    return expenses


@pytest.fixture
def overdue_debts(db_session, multiple_users):
    """Create overdue debts for testing"""
    debts = []
    for user in multiple_users:
        # Create overdue debt (due 5 days ago)
        overdue_debt = TestDataFactory.create_debt(
            user_id=user.id,
            name=f"Overdue Debt for {user.username}",
            amount=100.0,
            days_until_due=-5
        )
        db_session.add(overdue_debt)
        debts.append(overdue_debt)
    
    db_session.commit()
    return debts


@pytest.fixture
def upcoming_debts(db_session, multiple_users):
    """Create upcoming debts for testing"""
    debts = []
    for user in multiple_users:
        # Create upcoming debt (due in 7 days)
        upcoming_debt = TestDataFactory.create_debt(
            user_id=user.id,
            name=f"Upcoming Debt for {user.username}",
            amount=200.0,
            days_until_due=7
        )
        db_session.add(upcoming_debt)
        debts.append(upcoming_debt)
    
    db_session.commit()
    return debts
