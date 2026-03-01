def test_get_schemes(client):
    response = client.get("/api/v1/schemes/?state=Maharashtra&land_size_acres=5")
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == "Maharashtra"
    assert data["total_schemes"] > 0
    for scheme in data["schemes"]:
        assert "scheme_name" in scheme
        assert "scheme_name_hi" in scheme
        assert "how_to_apply" in scheme
        assert "eligibility" in scheme


def test_schemes_include_pm_kisan(client):
    response = client.get("/api/v1/schemes/?state=UP&land_size_acres=2")
    data = response.json()
    names = [s["scheme_name"] for s in data["schemes"]]
    assert "PM-KISAN" in names
    assert "PM Fasal Bima Yojana" in names
