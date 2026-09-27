def test_register_and_login(client):
    # 1. Test User Registration
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"email": "tester@example.com", "password": "pass123"},
    )
    assert reg_response.status_code == 201
    assert reg_response.json()["email"] == "tester@example.com"

    # 2. Test Login & Get Token (Using JSON)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "tester@example.com", "password": "pass123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"].lower() == "bearer"


def test_create_candidate_unauthorized(client):
    response = client.post(
        "/api/v1/candidates/",
        json={"name": "Rahul", "skill": "Python", "experience": 3},
    )
    assert response.status_code == 401


def test_full_candidate_workflow(client):
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={"email": "recruiter@example.com", "password": "pass123"},
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter@example.com", "password": "pass123"},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.json()}"
    
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Candidate
    post_res = client.post(
        "/api/v1/candidates/",
        json={"name": "Aman", "skill": "FastAPI", "experience": 2},
        headers=headers,
    )
    assert post_res.status_code == 201
    candidate_id = post_res.json()["id"]

    # 2. Search Candidate by Skill
    search_res = client.get("/api/v1/candidates/search?skill=FastAPI")
    assert search_res.status_code == 200
    assert len(search_res.json()) >= 1

    # 3. Delete Candidate
    del_res = client.delete(f"/api/v1/candidates/{candidate_id}", headers=headers)
    assert del_res.status_code == 200