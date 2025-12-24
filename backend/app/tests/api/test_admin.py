import pytest
import shutil
from httpx import AsyncClient
from app.api import deps

# We need to simulate Superuser for these tests.
# Since we don't have a robust way to mock the token with "is_superuser" claim easily without modifying security/deps logic deeply or creating a real superuser in DB.
# For simplicity, we can try to override `get_current_active_superuser`.

@pytest.fixture(scope="function")
async def override_superuser_dependency(client: AsyncClient):
    from app.models import User
    # Mock user object
    class MockUser:
        id = 1
        is_active = True
        is_superuser = True
        email = "admin@example.com"

    async def mock_get_current_active_superuser():
        return MockUser()

    from app.main import app
    app.dependency_overrides[deps.get_current_active_superuser] = mock_get_current_active_superuser
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_file_upload(client: AsyncClient, override_superuser_dependency):
    # Prepare a file
    files = {'file': ('test.txt', b'test content', 'text/plain')}
    response = await client.post("/api/v1/files/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data["url"].startswith("/static/")

@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, override_superuser_dependency):
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# We need to create data first to test delete/update.
# Since dependency override is active, we can assume we are superuser.
# But we need real DB IDs.

@pytest.mark.asyncio
async def test_admin_poi_lifecycle(client: AsyncClient, override_superuser_dependency):
    # Create POI (POST /pois/ is also superuser only, so we can use it)
    poi_data = {
        "title": "Admin Test POI",
        "latitude": 55.0,
        "longitude": 37.0
    }
    response = await client.post("/api/v1/pois/", json=poi_data)
    assert response.status_code == 200
    poi_id = response.json()["id"]

    # Update POI
    update_data = {"title": "Updated Admin POI"}
    response = await client.put(f"/api/v1/pois/{poi_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Admin POI"

    # Delete POI
    response = await client.delete(f"/api/v1/pois/{poi_id}")
    assert response.status_code == 200
    
    # Verify gone
    response = await client.get(f"/api/v1/pois/{poi_id}")
    assert response.status_code == 404
