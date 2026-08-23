# tests for analytics summary calculations
def _register_and_login(client, email="analyticsuser@example.com"):
    client.post("/api/v1/auth/register", json={
        "full_name": "Analytics User",
        "email": email,
        "password": "password123"})
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "password123"
    })
    return response.json()["access_token"]



#=== user analytics 

#  reject requests with no token
def test_analytics_requires_auth(client):
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code in (401, 403)


def test_analytics_summary_empty(client):
    token = _register_and_login(client)

    response = client.get("/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["total_applications"] == 0
    assert data["conversion_rate"] == 0.0


def test_analytics_summary_calculates_correctly(client):
    token = _register_and_login(client, email="mathuser@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # for 3 applied, 1 interview
    for i in range(3):
        client.post("/api/v1/jobs/", json={
            "company_name": f"Company {i}",
            "job_title": "Role",
            "applied_date": "2024-01-01"
        }, headers=headers)

    client.post("/api/v1/jobs/", json={
        "company_name": "Interview Co",
        "job_title": "Role",
        "status": "interview",
        "applied_date": "2024-01-01"
    }, headers=headers)

    response = client.get("/api/v1/analytics/summary", headers=headers)
    data = response.json()

    assert data["total_applications"] == 4
    assert data["status_breakdown"]["applied"] == 3
    assert data["status_breakdown"]["interview"] == 1
    assert data["conversion_rate"] == 25.0


def test_analytics_excludes_soft_deleted_applications(client):
    token = _register_and_login(client, email="deleteuser@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post("/api/v1/jobs/", json={
        "company_name": "Delete Co",
        "job_title": "Role",
        "applied_date": "2024-01-01"
    }, headers=headers)
    application_id = create_response.json()["id"]

    client.delete(f"/api/v1/jobs/{application_id}", headers=headers)

    response = client.get("/api/v1/analytics/summary", headers=headers)
    assert response.json()["total_applications"] == 0


#Ctesting for user A analytics should never include User B applications
def test_analytics_only_counts_own_applications(client):
    token_a = _register_and_login(client, email="analyticsa@example.com")
    token_b = _register_and_login(client, email="analyticsb@example.com")

    for i in range(2):
        client.post("/api/v1/jobs/", json={
            "company_name": f"A Company {i}",
            "job_title": "Role",
            "applied_date": "2024-01-01"
        }, headers={"Authorization": f"Bearer {token_a}"})

    for i in range(5):
        client.post("/api/v1/jobs/", json={
            "company_name": f"B Company {i}",
            "job_title": "Role",
            "applied_date": "2024-01-01"
        }, headers={"Authorization": f"Bearer {token_b}"})

    response = client.get("/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token_a}"})
    assert response.json()["total_applications"] == 2



#============ Admin analytics
def test_admin_analytics_requires_admin_role(client):
    token = _register_and_login(client, email="notadmin@example.com")
    response = client.get("/api/v1/analytics/admin/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_admin_analytics_includes_all_users_data(client, engine):
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User, UserRole

    token_a = _register_and_login(client, email="platformusera@example.com")
    _register_and_login(client, email="platformadmin@example.com")

    TestSession = sessionmaker(bind=engine)
    db = TestSession()
    user = db.query(User).filter(User.email == "platformadmin@example.com").first()
    user.role = UserRole.admin
    db.commit()
    db.close()

    login_response = client.post("/api/v1/auth/login", json={
        "email": "platformadmin@example.com",
        "password": "password123"
    })
    admin_token = login_response.json()["access_token"]

    for i in range(3):
        client.post("/api/v1/jobs/", json={
            "company_name": f"Platform Company {i}",
            "job_title": "Role",
            "applied_date": "2024-01-01"
        }, headers={"Authorization": f"Bearer {token_a}"})

    client.post("/api/v1/jobs/", json={
        "company_name": "Admin Company",
        "job_title": "Role",
        "applied_date": "2024-01-01"
    }, headers={"Authorization": f"Bearer {admin_token}"})

    response = client.get("/api/v1/analytics/admin/summary",
        headers={"Authorization": f"Bearer {admin_token}"})

    assert response.json()["total_applications"] == 4