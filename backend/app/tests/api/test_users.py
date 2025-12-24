import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_user_me(client: AsyncClient):
    import uuid
    uid = str(uuid.uuid4())
    email = f"me_{uid}@example.com"
    username = f"me_{uid}"
    password = "password"
    
    await client.post(
        "/api/v1/register",
        json={"email": email, "username": username, "password": password},
    )
    
    login_resp = await client.post(
        "/api/v1/login/access-token", 
        data={"username": username, "password": password}
    )
    token = login_resp.json()["access_token"]
    
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["username"] == username

@pytest.mark.asyncio
async def test_update_user_me(client: AsyncClient):
    import uuid
    uid = str(uuid.uuid4())
    email = f"upd_{uid}@example.com"
    username = f"upd_{uid}"
    password = "password"
    
    await client.post(
        "/api/v1/register",
        json={"email": email, "username": username, "password": password},
    )
    
    login_resp = await client.post(
        "/api/v1/login/access-token", 
        data={"username": username, "password": password}
    )
    token = login_resp.json()["access_token"]
    
    new_bio = "I am a chrono walker"
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"bio": new_bio}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == new_bio
