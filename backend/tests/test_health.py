"""Tests for health check endpoint."""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"
    assert data["data"]["status"] == "healthy"
