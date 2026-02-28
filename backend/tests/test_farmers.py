FARMER_DATA = {
    "name": "Ramesh Kumar",
    "phone": "9876543210",
    "state": "Madhya Pradesh",
    "district": "Indore",
    "village": "Sanwer",
    "latitude": 22.7196,
    "longitude": 75.8577,
    "land_size_acres": 5.0,
    "soil_type": "black",
    "irrigation_source": "borewell",
    "language": "hi",
}


def test_register_farmer(client):
    response = client.post("/api/v1/farmers/", json=FARMER_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ramesh Kumar"
    assert data["phone"] == "9876543210"
    assert data["state"] == "Madhya Pradesh"
    assert data["soil_type"] == "black"
    assert "id" in data


def test_register_duplicate_phone(client):
    client.post("/api/v1/farmers/", json=FARMER_DATA)
    response = client.post("/api/v1/farmers/", json=FARMER_DATA)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_get_farmer(client):
    create = client.post("/api/v1/farmers/", json=FARMER_DATA)
    farmer_id = create.json()["id"]
    response = client.get(f"/api/v1/farmers/{farmer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Ramesh Kumar"


def test_get_farmer_not_found(client):
    response = client.get("/api/v1/farmers/999")
    assert response.status_code == 404


def test_update_farmer(client):
    create = client.post("/api/v1/farmers/", json=FARMER_DATA)
    farmer_id = create.json()["id"]
    response = client.put(
        f"/api/v1/farmers/{farmer_id}",
        json={"land_size_acres": 10.0, "irrigation_source": "canal"},
    )
    assert response.status_code == 200
    assert response.json()["land_size_acres"] == 10.0
    assert response.json()["irrigation_source"] == "canal"


def test_get_farmer_by_phone(client):
    client.post("/api/v1/farmers/", json=FARMER_DATA)
    response = client.get("/api/v1/farmers/phone/9876543210")
    assert response.status_code == 200
    assert response.json()["phone"] == "9876543210"


def test_register_farmer_invalid_phone(client):
    invalid = {**FARMER_DATA, "phone": "123"}
    response = client.post("/api/v1/farmers/", json=invalid)
    assert response.status_code == 422
