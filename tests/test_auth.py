import pytest
from flask import url_for


class TestAuthentication:
    """Test cases for authentication routes"""

    @pytest.mark.integration
    def test_login_page_get(self, client):
        """Test accessing login page"""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()

    @pytest.mark.integration
    def test_login_success(self, client, sample_user):
        """Test successful login"""
        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpassword"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to index after successful login
        assert b"dashboard" in response.data.lower() or b"index" in response.data.lower() or b"gastos" in response.data.lower()

    @pytest.mark.integration
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post("/login", data={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data or b"incorrect" in response.data

    @pytest.mark.integration
    def test_login_already_authenticated(self, authenticated_client):
        """Test login when already authenticated"""
        response = authenticated_client.get("/login", follow_redirects=True)
        # Should redirect to index
        assert response.status_code == 200

    @pytest.mark.integration
    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()

    @pytest.mark.integration
    def test_protected_route_redirect(self, client):
        """Test that protected routes redirect to login"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert b"sesion" in response.data.lower() or b"iniciar" in response.data.lower()

    @pytest.mark.integration
    def test_session_data_after_login(self, client, sample_user):
        """Test that session data is set correctly after login"""
        with client.session_transaction() as sess:
            # Initially no session data
            assert "user_id" not in sess

        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpassword"
        })

        with client.session_transaction() as sess:
            # After login, session should have user data
            assert sess["user_id"] == sample_user.id
            assert sess["username"] == "testuser"
            assert sess["is_admin"] is False
