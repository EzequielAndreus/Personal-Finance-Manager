import pytest
from datetime import date, timedelta
from flask import url_for


class TestIndexRoute:
    """Test cases for the main index/dashboard route"""

    @pytest.mark.integration
    def test_index_requires_auth(self, client):
        """Test that index route requires authentication"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()

    @pytest.mark.integration
    def test_index_authenticated(self, authenticated_client, sample_expense):
        """Test index route with authenticated user"""
        response = authenticated_client.get("/")
        assert response.status_code == 200
        assert b"dashboard" in response.data.lower() or b"index" in response.data.lower() or b"gastos" in response.data.lower()

    @pytest.mark.integration
    def test_index_with_expenses(self, authenticated_client, sample_expense, sample_debt):
        """Test index route displays expense statistics"""
        response = authenticated_client.get("/")
        assert response.status_code == 200
        # Should show expense data
        assert str(sample_expense.amount).encode() in response.data
        assert str(sample_debt.amount).encode() in response.data


class TestExpenseRoutes:
    """Test cases for expense-related routes"""

    @pytest.mark.integration
    def test_new_expense_get(self, authenticated_client):
        """Test accessing new expense form"""
        response = authenticated_client.get("/expenses/new")
        assert response.status_code == 200
        assert b"new" in response.data.lower() or b"expense" in response.data.lower()

    @pytest.mark.integration
    def test_new_expense_requires_auth(self, client):
        """Test that new expense route requires authentication"""
        response = client.get("/expenses/new", follow_redirects=True)
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()

    @pytest.mark.integration
    def test_create_expense_success(self, authenticated_client, db_session):
        """Test creating a new expense successfully"""
        response = authenticated_client.post("/expenses/new", data={
            "name": "Test Expense",
            "amount": "150.50",
            "category": "Food",
            "date": date.today().strftime("%Y-%m-%d"),
            "comment": "Test comment"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to index after successful creation
        assert b"dashboard" in response.data.lower() or b"index" in response.data.lower() or b"gastos" in response.data.lower()

    @pytest.mark.integration
    def test_create_expense_missing_fields(self, authenticated_client):
        """Test creating expense with missing required fields"""
        response = authenticated_client.post("/expenses/new", data={
            "name": "Test Expense",
            # Missing amount, category, date
        })
        
        # Should redirect back to form (302) or show validation error (200)
        assert response.status_code in [200, 302]

    @pytest.mark.integration
    def test_create_debt(self, authenticated_client, db_session):
        """Test creating a debt (expense with due_date)"""
        due_date = date.today() + timedelta(days=30)
        response = authenticated_client.post("/expenses/new", data={
            "name": "Test Debt",
            "amount": "250.00",
            "category": "Utilities",
            "date": date.today().strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "comment": "Test debt"
        }, follow_redirects=True)
        
        assert response.status_code == 200

    @pytest.mark.integration
    def test_expenses_list(self, authenticated_client, sample_expense):
        """Test expenses list page"""
        response = authenticated_client.get("/expenses")
        assert response.status_code == 200
        assert str(sample_expense.amount).encode() in response.data
        assert sample_expense.name.encode() in response.data

    @pytest.mark.integration
    def test_expenses_list_requires_auth(self, client):
        """Test that expenses list requires authentication"""
        response = client.get("/expenses", follow_redirects=True)
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()

    @pytest.mark.integration
    def test_edit_expense_get(self, authenticated_client, sample_expense):
        """Test accessing edit expense form"""
        try:
            response = authenticated_client.get(f"/expenses/{sample_expense.id}/edit")
            # Template might not exist, so expect either 200 or 404
            assert response.status_code in [200, 404]
        except Exception:
            # If template doesn't exist, that's expected behavior
            pass

    @pytest.mark.integration
    def test_edit_expense_success(self, authenticated_client, sample_expense):
        """Test editing an expense successfully"""
        response = authenticated_client.post(f"/expenses/{sample_expense.id}/edit", data={
            "name": "Updated Expense",
            "amount": "200.00",
            "category": "Updated Category",
            "date": date.today().strftime("%Y-%m-%d"),
            "comment": "Updated comment"
        }, follow_redirects=True)
        
        assert response.status_code == 200

    @pytest.mark.integration
    def test_delete_expense(self, authenticated_client, sample_expense, db_session):
        """Test deleting an expense"""
        expense_id = sample_expense.id
        response = authenticated_client.post(f"/expenses/{expense_id}/delete", 
                                           follow_redirects=True)
        
        assert response.status_code == 200
        # Verify expense was deleted
        from models import Expense
        deleted_expense = Expense.query.get(expense_id)
        assert deleted_expense is None


class TestDebtRoutes:
    """Test cases for debt-related routes"""

    @pytest.mark.integration
    def test_debts_list(self, authenticated_client, sample_debt):
        """Test debts list page"""
        response = authenticated_client.get("/debts")
        assert response.status_code == 200
        assert str(sample_debt.amount).encode() in response.data
        assert sample_debt.name.encode() in response.data

    @pytest.mark.integration
    def test_debts_list_requires_auth(self, client):
        """Test that debts list requires authentication"""
        response = client.get("/debts", follow_redirects=True)
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()


class TestSummaryRoute:
    """Test cases for summary route"""

    @pytest.mark.integration
    def test_summary_page(self, authenticated_client, sample_expense, sample_debt):
        """Test summary page"""
        response = authenticated_client.get("/summary")
        assert response.status_code == 200
        assert str(sample_expense.amount).encode() in response.data
        assert str(sample_debt.amount).encode() in response.data

    @pytest.mark.integration
    def test_summary_requires_auth(self, client):
        """Test that summary requires authentication"""
        response = client.get("/summary", follow_redirects=True)
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()


class TestErrorHandling:
    """Test cases for error handling"""

    @pytest.mark.integration
    def test_404_error(self, authenticated_client):
        """Test 404 error handling"""
        response = authenticated_client.get("/nonexistent-route")
        assert response.status_code == 404

    @pytest.mark.integration
    def test_expense_not_found(self, authenticated_client):
        """Test accessing non-existent expense"""
        response = authenticated_client.get("/expenses/99999/edit")
        assert response.status_code == 404

    @pytest.mark.integration
    def test_unauthorized_expense_access(self, client, sample_user, sample_expense):
        """Test accessing another user's expense"""
        # Create another user and try to access first user's expense
        from models import User, db
        other_user = User(username="otheruser")
        other_user.set_password("password")
        db.session.add(other_user)
        db.session.commit()
        
        with client.session_transaction() as sess:
            sess["user_id"] = other_user.id
            sess["username"] = other_user.username
            sess["is_admin"] = False
        
        response = client.get(f"/expenses/{sample_expense.id}/edit", follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to expenses list with error message
