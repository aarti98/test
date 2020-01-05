from ..models import Location
import logging
import pytest


def test_get_location(test_client, location_factory):
    location = location_factory()
    params = {"latitude": location.latitude, "longitude": location.longitude}
    response = test_client.get(
        "/get_location/", headers={"accept": "application/json"}, params=params
    )
    assert response.status_code == 200


def test_create_location(test_client):
    data = {
        "id": "123,1321",
        "place_name": "place_name_test",
        "admin_name1": "place_admin_name1",
        "latitude": 13.1331,
        "longitude": 15.1551,
        "accuracy": 1,
    }
    response = test_client.post(
        "/post_location/", headers={"accept": "application/json"}, json=data
    )
    assert response.status_code == 201


def test_get_location_by_radius():
    pass


def test_get_location_by_self():
    pass


def test_get_place():
    pass
