FARMER_DATA = {
    "name": "Suresh Patel",
    "phone": "9988776655",
    "state": "Gujarat",
    "district": "Ahmedabad",
    "land_size_acres": 3.0,
    "soil_type": "loamy",
    "language": "gu",
}

DIARY_ENTRY = {
    "crop_name": "Wheat",
    "activity": "Applied DAP fertiliser",
    "category": "fertiliser",
    "expense_amount": 1500.0,
    "income_amount": 0,
    "notes": "50kg DAP at ₹30/kg",
    "season": "rabi-2024",
}


def test_add_diary_entry(client):
    farmer = client.post("/api/v1/farmers/", json=FARMER_DATA).json()
    response = client.post(f"/api/v1/diary/{farmer['id']}", json=DIARY_ENTRY)
    assert response.status_code == 201
    data = response.json()
    assert data["crop_name"] == "Wheat"
    assert data["expense_amount"] == 1500.0
    assert data["category"] == "fertiliser"


def test_list_diary_entries(client):
    farmer = client.post("/api/v1/farmers/", json=FARMER_DATA).json()
    client.post(f"/api/v1/diary/{farmer['id']}", json=DIARY_ENTRY)
    client.post(
        f"/api/v1/diary/{farmer['id']}",
        json={**DIARY_ENTRY, "activity": "Irrigation", "category": "irrigation", "expense_amount": 500},
    )
    response = client.get(f"/api/v1/diary/{farmer['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_season_summary(client):
    farmer = client.post("/api/v1/farmers/", json=FARMER_DATA).json()
    fid = farmer["id"]
    client.post(f"/api/v1/diary/{fid}", json=DIARY_ENTRY)
    client.post(
        f"/api/v1/diary/{fid}",
        json={
            "crop_name": "Wheat",
            "activity": "Sold harvest",
            "category": "sale",
            "expense_amount": 0,
            "income_amount": 25000.0,
            "season": "rabi-2024",
        },
    )
    response = client.get(
        f"/api/v1/diary/{fid}/summary?season=rabi-2024&crop_name=Wheat"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_expenses"] == 1500.0
    assert data["total_income"] == 25000.0
    assert data["net_profit"] == 23500.0
    assert data["entries_count"] == 2


def test_diary_farmer_not_found(client):
    response = client.post("/api/v1/diary/999", json=DIARY_ENTRY)
    assert response.status_code == 404
