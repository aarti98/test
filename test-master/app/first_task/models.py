from sqlalchemy import Column, Integer, String, Float, BigInteger, func
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from .database import Base

import math


class Location(Base):
    __tablename__ = "data_location"

    id = Column(String(20), primary_key=True, nullable=False)
    place_name = Column(String(100), nullable=False)
    admin_name1 = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Integer)

    # @property
    # def earth_distance(self):
    #     return func.ll_to_earth(self.latitude, self.longitude)
    #
    # @hybrid_method
    # def great_circle_distance(self, other):
    #     """
    #     Tries to calculate the great circle distance between
    #     the two locations by using the Haversine formula.
    #
    #     If it succeeds, it will return the Haversine formula
    #     multiplied by 3959, which calculates the distance in miles.
    #
    #     If it cannot, it will return None.
    #
    #     """
    #     return math.acos(  self.cos_rad_lat
    #                      * other.cos_rad_lat
    #                      * math.cos(self.rad_lng - other.rad_lng)
    #                      + self.sin_rad_lat
    #                      * other.sin_rad_lat
    #                      ) * 3959
    #
    # @great_circle_distance.expression
    # def great_circle_distance(cls, other):
    #     return func.acos(  cls.cos_rad_lat
    #                      * other.cos_rad_lat
    #                      * sqlalchemy.func.cos(cls.rad_lng - other.rad_lng)
    #                      + cls.sin_rad_lat
    #                      * other.sin_rad_lat
    #                      ) * 3959
class City(Base):
    __tablename__ = "city_location"
    id = Column(BigInteger, primary_key=True, nullable=False)
    city = Column(String(100), nullable=False)
    lat = Column(Float)
    long = Column(Float)
