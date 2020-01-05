import pytest
import uuid

from functools import partial
from sqlalchemy.orm import scoped_session, sessionmaker

from ..models import Location, City

from ..main import app, get_db_session
from .. import database

from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy import create_engine

from starlette.config import environ
from starlette.testclient import TestClient

# This sets `os.environ`, but provides some additional protection.
# If we placed it below the application import, it would raise an error
# informing us that 'TESTING' had already been read from the environment.

environ["TESTING"] = "True"
environ["EMAILS_ENABLED"] = "False"


def _make_test_obj(session, entity, **kwargs):
    obj = entity(**kwargs)
    session.add(obj)
    session.flush()
    return obj


def _create_lookup(db_session, factory, mapping, values):
    for value in values:
        factory(db_session, mapping, name=value)


@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///")
    database.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    return scoped_session(
        sessionmaker(bind=db_engine, autocommit=False, autoflush=True)
    )


@pytest.fixture(scope="module")
def obj_factory():
    return _make_test_obj


@pytest.fixture
def factory(db_session):
    return partial(_make_test_obj, db_session)


@pytest.fixture
def test_app(db_session):
    setattr(app, "db", lambda: db_session)


def _create_location(
    factory,
    id_=None,
    latitude=None,
    longitude=None,
    admin_name1=None,
    place_name=None,
    accuracy=None,
):
    id_ = str(uuid.uuid4()) if id_ is None else id_
    latitude = 10 if latitude is None else latitude
    longitude = 11 if longitude is None else longitude
    admin_name1 = "admin_name" if admin_name1 is None else admin_name1
    accuracy = "accuracy" if accuracy is None else accuracy
    place_name = "place_name" if place_name is None else place_name

    location = factory(
        Location,
        id=id_,
        accuracy=accuracy,
        admin_name1=admin_name1,
        latitude=latitude,
        longitude=longitude,
        place_name=place_name,
    )
    return location

@pytest.fixture
def location_factory(factory):
    return partial(_create_location, factory)

@pytest.fixture
def location_1(db_session, factory):
    guid = str(uuid.uuid4())
    location = factory(
        Location,
        accuracy=1,
        admin_name1="test_name",
        latitude=12.12,
        longitude=23.23,
        place_name="test_place_name",
        id=guid,
    )
    return location


# @pytest.fixture(scope="session", autouse=True)
# def create_test_database():
#     url = str("sqlite:///")
#     engine = create_engine(url)
#     if database_exists(url):
#         drop_database(url)
#     create_database(url)  # Create the test database.
#     database.Base.metadata.create_all(engine)  # Create the tables.
#     yield  # Run the tests.
#     drop_database(url)  # Drop the test database.


@pytest.fixture
def test_client():
    app.dependency_overrides[get_db_session] = db_session
    client = TestClient(app)
    return client


## Helpers ##
def get_uuid():
    return str(uuid.uuid4())
