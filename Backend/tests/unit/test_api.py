import pytest
import httpx
from app.main import app

# AsyncClient + ASGITransport (sync Client not supported with async transport in current httpx)
transport = httpx.ASGITransport(app=app)


@pytest.fixture
async def client():
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Loan Assessment API"


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_application_endpoint_exists():
    """Test that create application endpoint is defined"""
    # Verify the applications router is mounted (full integration would require async DB)
    def path_contains(r, s):
        p = getattr(r, "path", None) or getattr(r, "path_regex", None)
        return p and s in str(p)
    assert any(path_contains(r, "application") for r in app.routes)
