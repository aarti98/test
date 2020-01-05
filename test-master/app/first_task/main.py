from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response
from celery import Celery
from app.first_task import crud, models
from app.first_task import schemas
from app.first_task.database import SessionLocal, engine
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

BROKER_URL = "redis://localhost:6379/0"
celery = Celery("main", broker=BROKER_URL)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db_session = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db_session.close()
    return response


def get_db_session(request: Request):
    return request.state.db_session


@app.get("/get_location/", response_model=schemas.Location)
def get_location(
    latitude: float, longitude: float, db: Session = Depends(get_db_session)
):
    location = crud.get_location_by_lat_long(db, latitude=latitude, longitude=longitude)

    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    return location


@app.post("/post_location/", response_model=schemas.Location)
def create_location(
    location: schemas.LocationCreate, db: Session = Depends(get_db_session)
):
    db_location = crud.get_location_by_pincode(db, pincode=location.id)
    db_lat_long = crud.get_location_by_lat_long(
        db, latitude=location.latitude, longitude=location.longitude
    )
    create_location.apply_async(4,4)

    if db_location:
        raise HTTPException(status_code=400, detail="Pincode already exists")

    if db_lat_long:
        raise HTTPException(status_code=400, detail="Location already exists")

    return crud.add_pincode(db=db, location=location)


@app.get("/get_using_postgres/", response_model=schemas.Location)
def get_location_by_radius(
    latitude: float,
    longitude: float,
    radius: float,
    db: Session = Depends(get_db_session),
):
    location = crud.get_pincode_within_radius(
        db, lat=latitude, long=longitude, radius=radius
    )
    return location


@app.get("/get_using_self/", response_model=schemas.Location)
def get_location_by_self(
    latitude: float, longitude: float, db: Session = Depends(get_db_session)
):
    location = crud.get_pincode_by_self(db, latitude=latitude, longitude=longitude)
    # db_session(location)
    return location


@app.get("/detect/", response_model=schemas.City)
def get_place(lat: float, long: float, db: Session = Depends(get_db_session)):
    city = crud.get_city_by_latitude(db, lat=lat, long=long)
    return city


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
