# tests for job applications crud 

def _register_and_login(client, email="jobsuser@example.com"):
    client.post("/api/v1/auth/register", json={
        "full_name": "Jobs User",
        "email": email,
        "password": "password123"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "password123"})
    return response.json()["access_token"]

#application can not create without a valid token."""
def test_create_application_requires_auth(client):
    response = client.post("/api/v1/jobs/", json={
        "company_name": "Google",
        "job_title": "Backend Engineer",
        "applied_date": "2024-01-15"
    })
    assert response.status_code in (401, 403)


def test_create_application_success(client):
    token = _register_and_login(client)
    response = client.post("/api/v1/jobs/",
        json={"company_name": "Google","job_title": "Backend Engineer","applied_date": "2024-01-15"},
        headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Google"
    assert data["status"] == "applied" 

# testing for user A should never see user b applications 
def test_get_all_applications_only_shows_own(client):
    token_a = _register_and_login(client, email="usera@example.com")
    token_b = _register_and_login(client, email="userb@example.com")

    # user A creates an application
    client.post("/api/v1/jobs/",
        json={"company_name": "Company A", "job_title": "role A", "applied_date": "2024-01-01"},
        headers={"Authorization": f"Bearer {token_a}"})

    # user B creates a different application
    client.post("/api/v1/jobs/",
        json={"company_name": "Company B", "job_title": "role B", "applied_date": "2024-01-02"},
        headers={"Authorization": f"Bearer {token_b}"})

    # User A fetches their applications — should see ONLY their own
    response = client.get("/api/v1/jobs/",headers={"Authorization": f"Bearer {token_a}"})

    data = response.json()
    assert data["total"] == 1
    assert data["applications"][0]["company_name"] == "Company A"

# user A cannot fetch user B specific application by ID
def test_cannot_access_another_users_application(client):
    
    token_a = _register_and_login(client, email="ownera@example.com")
    token_b = _register_and_login(client, email="ownerb@example.com")

    # user B creates an application
    create_response = client.post("/api/v1/jobs/",
        json={"company_name": "Secret Corp", "job_title": "Secret Role", "applied_date": "2024-01-01"},
        headers={"Authorization": f"Bearer {token_b}"})
    
    application_id = create_response.json()["id"]

    # user A tries to access user B application directly by id
    response = client.get(f"/api/v1/jobs/{application_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 404


def test_update_application_partial_update(client):
    token = _register_and_login(client, email="updateuser@example.com")

    create_response = client.post(
        "/api/v1/jobs/",
        json={"company_name": "Amazon", "job_title": "SDE", "applied_date": "2024-01-01"},
        headers={"Authorization": f"Bearer {token}"}
    )
    application_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/jobs/{application_id}",
        json={"status": "interview"},
        headers={"Authorization": f"Bearer {token}"}
    )

    data = update_response.json()
    assert data["status"] == "interview"
    assert data["company_name"] == "Amazon"

# testing for soft delete
def test_soft_delete_hides_application(client):
    token = _register_and_login(client, email="deleteuser@example.com")

    create_response = client.post("/api/v1/jobs/",
        json={"company_name": "Meta", "job_title": "Engineer", "applied_date": "2024-01-01"},
        headers={"Authorization": f"Bearer {token}"} )
    application_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/jobs/{application_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204


    get_response = client.get(
        f"/api/v1/jobs/{application_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404

    # testing delete on another user's application is blocked
def test_cannot_delete_another_users_application(client):
    token_a = _register_and_login(client, email="deleteownera@example.com")
    token_b = _register_and_login(client, email="deleteownerb@example.com")

    create_response = client.post("/api/v1/jobs/",
        json={"company_name": "Spotify", "job_title": "Engineer", "applied_date": "2024-01-01"},
        headers={"Authorization": f"Bearer {token_b}"})
    application_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/jobs/{application_id}",
        headers={"Authorization": f"Bearer {token_a}"})

    assert response.status_code == 404