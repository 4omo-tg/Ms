import pytest
import uuid
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_leaderboard(client: AsyncClient):
    # Leaderboard is public in our implementation
    response = await client.get("/api/v1/users/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # If we had seeded data, we could check order. 
    # Since DB is fresh per test function (due to our conftest), it might be empty or contain just created users.
    # Let's create users via header/auth if possilbe, or we need a way to seed XP.
    # Currently we can't easily set XP via API (it's internal).
    # We can trust the SQL `order_by` for now or need a backdoor/fixture to seed users with XP.
    # Given the constraints, a 200 OK and list response is a basic smoke test.

@pytest.mark.asyncio
async def test_nearby_pois(client: AsyncClient):
    # Need to check if PostGIS functions work.
    # We need to Seed POIs.
    # Create POI endpoint requires Superuser.
    # Creating a superuser via API is hard without a pre-existing one.
    # But we can try to hit the public endpoint with parameters.
    
    # Red Square, Moscow
    lat = 55.7539
    lon = 37.6208
    
    response = await client.get(f"/api/v1/pois/?latitude={lat}&longitude={lon}&radius=1000")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
