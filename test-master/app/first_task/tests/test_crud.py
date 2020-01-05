import pytest
import uuid
from ..crud import get_location_by_lat_long, get_location_by_pincode, add_pincode
from ..models import Location
from ..schemas import LocationCreate
def test_get_location(db_session, location_1):
    assert get_location_by_lat_long(
        latitude=location_1.latitude, longitude=location_1.longitude, db=db_session
    )


def test_get_location_by_pincode(db_session, location_1):
    assert get_location_by_lat_long(
        latitude=location_1.latitude, longitude=location_1.longitude, db=db_session
    )


def test_add_pincode_non_existing(
    db_session,
    location_factory,
    id_=str(uuid.uuid4()),
    latitude=999.00,
    longitude=111.00,
    admin_name1="test",
    place_name="test_city",
    accuracy=1,
):
    location = LocationCreate(
    id=id_,
    latitude=latitude,
    longitude=longitude,
    admin_name1=admin_name1,
    place_name=place_name,
    accuracy=accuracy,
    )
    add_pincode(db_session, location=location)
    assert db_session.query(Location).get(id_) is not None

