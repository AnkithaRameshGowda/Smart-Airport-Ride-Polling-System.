from pydantic import BaseModel


class PassengerCreate(BaseModel):
    name: str
    luggage: int
    seats_required: int
    source_lat: float
    source_lng: float
    dest_lat: float
    dest_lng: float
    detour_tolerance: float
