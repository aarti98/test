from pydantic import BaseModel


class LocationBase(BaseModel):
    id: str
    place_name: str
    admin_name1: str
    latitude: float
    longitude: float


class LocationCreate(LocationBase):
    latitude: float


class Location(LocationBase):
    id: str

    class Config:
        orm_mode = True


class CityBase(BaseModel):
    id: int
    city: str
    lat: float
    long: float


class CityCreate(CityBase):
    pass


class City(CityBase):
    id: int

    class Config:
        orm_mode = True
