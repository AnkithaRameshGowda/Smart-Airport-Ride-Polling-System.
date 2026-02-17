from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PoolStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FULL = "FULL"
    CANCELLED = "CANCELLED"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    total_seats = Column(Integer, nullable=False)
    luggage_capacity = Column(Integer, nullable=False)


class RidePool(Base):
    __tablename__ = "ride_pools"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    status = Column(Enum(PoolStatus), default=PoolStatus.ACTIVE, index=True)

    passengers = relationship("Passenger", back_populates="ride_pool")


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    luggage = Column(Integer, nullable=False)
    seats_required = Column(Integer, nullable=False)

    source_lat = Column(Float, nullable=False)
    source_lng = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)

    detour_tolerance = Column(Float, nullable=False)

    ride_pool_id = Column(Integer, ForeignKey("ride_pools.id"), index=True)

    ride_pool = relationship("RidePool", back_populates="passengers")
