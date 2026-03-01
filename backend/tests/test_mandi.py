from datetime import date
from app.models.mandi import MandiPrice


def test_get_prices_empty(client):
    response = client.get("/api/v1/mandi/prices?crop_name=Wheat")
    assert response.status_code == 200
    assert response.json() == []


def test_get_prices_with_data(client, db_session):
    price = MandiPrice(
        crop_name="Wheat",
        mandi_name="Indore Mandi",
        state="Madhya Pradesh",
        district="Indore",
        min_price=2000,
        max_price=2500,
        modal_price=2200,
        price_date=date.today(),
    )
    db_session.add(price)
    db_session.commit()

    response = client.get("/api/v1/mandi/prices?crop_name=Wheat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["modal_price"] == 2200


def test_sell_recommendation_no_data(client):
    response = client.get(
        "/api/v1/mandi/sell-recommendation?crop_name=Rice&mandi_name=TestMandi"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommendation"] == "hold"
