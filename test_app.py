from app import app


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_stats():
    client = app.test_client()
    data = client.get("/stats").get_json()
    expected = {"cpu_percent", "memory_percent", "disk_percent", "per_cpu", "processes"}
    assert expected <= set(data)
    assert len(data["per_cpu"]) >= 1


def test_dashboard_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"System Monitor" in response.data
