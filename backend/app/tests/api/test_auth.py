import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    uid = str(uuid.uuid4())
    email = f"test_{uid}@example.com"
    username = f"user_{uid}"
    response = await client.post(
        "/api/v1/register",
        json={"email": email, "username": username, "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data

@pytest.mark.asyncio
async def test_login_access_token(client: AsyncClient):
    uid = str(uuid.uuid4())
    email = f"login_{uid}@example.com"
    username = f"login_{uid}"
    await client.post(
        "/api/v1/register",
        json={"email": email, "username": username, "password": "testpassword"},
    )
    
    login_data = {
        "username": username,
        "password": "testpassword",
    }
    response = await client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"
