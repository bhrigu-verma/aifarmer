def test_get_inputs_wheat(client):
    response = client.get("/api/v1/inputs/wheat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["crop_name"] == "wheat"
    stages = [s["stage_name"] for s in data]
    assert "Land Preparation" in stages
    assert "Harvesting" in stages


def test_get_inputs_rice(client):
    response = client.get("/api/v1/inputs/rice")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["crop_name"] == "rice"


def test_get_inputs_unknown_returns_general(client):
    response = client.get("/api/v1/inputs/mango")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stage_name"] == "General"
