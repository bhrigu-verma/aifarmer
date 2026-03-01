def test_recommend_crops(client):
    response = client.get("/api/v1/crops/recommend?soil_type=black&season=kharif")
    assert response.status_code == 200
    data = response.json()
    assert data["soil_type"] == "black"
    assert data["season"] == "kharif"
    assert len(data["recommendations"]) <= 3
    for rec in data["recommendations"]:
        assert "crop_name" in rec
        assert "expected_profit_per_acre" in rec
        assert "risk_level" in rec
        assert "suitability_score" in rec


def test_recommend_crops_rabi(client):
    response = client.get("/api/v1/crops/recommend?soil_type=alluvial&season=rabi")
    assert response.status_code == 200
    data = response.json()
    assert data["season"] == "rabi"
    assert len(data["recommendations"]) > 0


def test_input_guide_wheat(client):
    response = client.get("/api/v1/crops/inputs/wheat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["crop_name"] == "wheat"
    assert "stage_name" in data[0]
    assert "estimated_cost" in data[0]


def test_input_guide_unknown_crop(client):
    response = client.get("/api/v1/crops/inputs/dragonfruit")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stage_name"] == "General"
