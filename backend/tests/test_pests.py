import io


def test_list_diseases(client):
    response = client.get("/api/v1/pests/diseases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "leaf_blight" in data
    assert "powdery_mildew" in data


def test_get_disease_info(client):
    response = client.get("/api/v1/pests/diseases/leaf_blight")
    assert response.status_code == 200
    data = response.json()
    assert data["disease_name"] == "Leaf Blight"
    assert data["severity"] == "moderate"
    assert len(data["treatment"]) > 0


def test_get_disease_not_found(client):
    response = client.get("/api/v1/pests/diseases/unknown_disease")
    assert response.status_code == 404


def test_detect_disease_with_image(client):
    image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    response = client.post(
        "/api/v1/pests/detect",
        files={"image": ("test.png", io.BytesIO(image_content), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "disease_name" in data
    assert "confidence" in data
    assert data["confidence"] > 0
