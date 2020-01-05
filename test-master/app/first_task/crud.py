import psycopg2
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import text
from app.first_task import models
from app.first_task import schemas
from app.first_task.database import engine as db_engine
import json
import pandas as pd
import celery


host = "localhost"
name = "api"
password = "api"
db_name = "pincode"

conn = psycopg2.connect(
    host=host, user=name, password=password, dbname=db_name, connect_timeout=5
)


def get_location_by_lat_long(db: Session, latitude: float, longitude: float):
    return (
        db.query(models.Location)
        .filter(
            models.Location.latitude == latitude, models.Location.longitude == longitude
        )
        .first()
    )


def get_location_by_pincode(db: Session, pincode: str):
    return db.query(models.Location).filter(models.Location.id == pincode).first()

@celery.task
def add_pincode(db: Session, location: schemas.LocationCreate):

    db_location = models.Location(
        longitude=location.longitude,
        latitude=location.latitude,
        place_name=location.place_name,
        admin_name1=location.admin_name1,
        id=location.id,
    )

    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

from .database import engine
def get_pincode_within_radius(db: Session, lat: float, long: float, radius: float):
    # earth_location = func.ll_to_earth(lat, long)
    earth_box = func.earth_box(func.ll_to_earth(lat, long), radius)
    q = text(
        "SELECT id "
        "FROM data_location "
        "WHERE earth_box(ll_to_earth({}, {}), 5000) @> ll_to_earth(latitude, longitude);".format(lat, long)
    )
    with engine.connect() as con:
        d = con.execute(q)
    # engine.execute()
    location_obj = (
        db.query(models.Location)
        .filter(
            earth_box
            > func.ll_to_earth(models.Location.latitude, models.Location.longitude)
        )
        .first()
    )
    # WHERE earth_box( {current_user_lat}, {current_user_lng}, {radius_in_metres}) @> ll_to_earth(events.lat, events.lng);
    # query = 'SELECT id FROM location WHERE earth_box(ll_to_earth({}, {}), 5000) @> ll_to_earth(latitude, longitude);'.format(lat, long)
    return location_obj


def get_pincode_by_self(db: Session, latitude: float, longitude: float):
    c = conn.cursor()
    query = """select id from location where acos(sin(radians({0}))*sin(radians({0}))+cos(radians({0}))
            *cos(radians({0}))*cos(radians({1})-radians({1})))*6371<=5;""".format(
        latitude, longitude
    )
    values = c.execute(query)
    return values


def get_city_by_latitude(db: Session, lat: float, long: float):
    cur = conn.cursor()

    with open("geo.geojson") as f:
        d = json.load(f)
        values = pd.DataFrame(d)
        city_list = []
        for x in range(len(values["features"])):
            city = values["features"][x]["properties"]["name"]
            coordinates = values["features"][x]["geometry"]["coordinates"][0]
            city_list.append(city)

        latitude = []
        longitude = []

        for lat in range(0, len(coordinates)):
            latitude.append(coordinates[lat][0])
            longitude.append(coordinates[lat][1])
        result = zip(city_list, latitude, longitude)

        for x, y, z in result:
            cur.execute(
                """ INSERT INTO city_location('city', 'lat', 'long') VALUES('{}',{},{});""".format(
                    x, y, z
                )
            )

        conn.commit()
        cur.close()
    return (
        db.query(models.City)
        .filter(models.City.lat == lat, models.City.long == long)
        .first()
    )
