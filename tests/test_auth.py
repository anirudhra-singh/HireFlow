# tests for registration, login, and jwt

#== registarion related testing
class TestRegistration:
# new user registertion
    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"
        assert "hashed_password" not in data

    def test_register_duplicate_email_fails(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "Test User",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Another User",
            "email": "duplicate@example.com",
            "password": "differentpass"
        })

        assert response.status_code == 400

    def test_register_weak_password_fails(self, client):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Test User",
            "email": "weak@example.com",
            "password": "123"
        })
        assert response.status_code == 422



# == login related testing
class TestLogin:
    # user login testing
    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "Login User",
            "email": "login@example.com",
            "password": "password123"
        })
        response = client.post("/api/v1/auth/login", json={
            "email": "login@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

#for wrong password 
    def test_login_wrong_password_fails(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "Login User",
            "email": "wrongpass@example.com",
            "password": "correctpassword"
        })
        response = client.post("/api/v1/auth/login", json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

# unregistered email
    def test_login_nonexistent_email_fails(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "doesnotexist@example.com",
            "password": "anypassword"
        })
        assert response.status_code == 401



