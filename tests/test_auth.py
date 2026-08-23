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



# == Authorization related testing
class TestAuthorization:
    # user access 
    def test_get_me_without_token_fails(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code in (401, 403)

    def test_user_can_access_own_profile(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "Me User",
            "email": "me@example.com",
            "password": "password123"
        })
        login_response = client.post("/api/v1/auth/login", json={
            "email": "me@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]

        response = client.get("/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    def test_invalid_token_rejected(self, client):
        response = client.get("/api/v1/auth/me",
            headers={"Authorization": "Bearer this.is.not.a.real.token"}
        )
        assert response.status_code == 401


   
    # Admin access
    def test_user_cannot_access_admin_route(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "Regular User",
            "email": "regular@example.com",
            "password": "password123"
        })
        login_response = client.post("/api/v1/auth/login", json={
            "email": "regular@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        response = client.get(
            "/api/v1/analytics/admin/summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    def test_admin_can_access_admin_route(self, client, engine):
        from app.core.database import sessionmaker
        from app.models.user import User, UserRole

        client.post("/api/v1/auth/register", json={
            "full_name": "Admin User",
            "email": "admin@example.com",
            "password": "password123"
        })
        TestSession = sessionmaker(bind=engine)
        db = TestSession()
        user = db.query(User).filter(User.email == "admin@example.com").first()
        user.role = UserRole.admin
        db.commit()
        db.close()
        login_response = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "password123"
    })
        token = login_response.json()["access_token"]
        response = client.get(
        "/api/v1/analytics/admin/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
        assert response.status_code == 200

    # Role protection
    def test_regular_user_role_is_forced_on_register(self, client):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Sneaky User",
            "email": "sneaky@example.com",
            "password": "password123",
            "role": "admin"          
        })
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "user"