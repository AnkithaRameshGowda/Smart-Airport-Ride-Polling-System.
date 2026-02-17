import math
from sqlalchemy import select
from app.models import RidePool, Vehicle, Passenger, PoolStatus


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


async def match_passenger(db, passenger):

    result = await db.execute(
        select(RidePool)
        .where(RidePool.status == PoolStatus.ACTIVE)
        .with_for_update()
    )
    pools = result.scalars().all()

    best_pool = None
    min_deviation = float("inf")

    for pool in pools:

        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.id == pool.vehicle_id)
        )
        vehicle = vehicle_result.scalar_one()

        passengers_result = await db.execute(
            select(Passenger).where(Passenger.ride_pool_id == pool.id)
        )
        passengers = passengers_result.scalars().all()

        used_seats = sum(p.seats_required for p in passengers)
        used_luggage = sum(p.luggage for p in passengers)

        if (
            used_seats + passenger.seats_required > vehicle.total_seats
            or used_luggage + passenger.luggage > vehicle.luggage_capacity
        ):
            continue

        if passengers:
            avg_lat = sum(p.source_lat for p in passengers) / len(passengers)
            avg_lng = sum(p.source_lng for p in passengers) / len(passengers)

            deviation = haversine(
                avg_lat,
                avg_lng,
                passenger.source_lat,
                passenger.source_lng
            )

            if deviation > passenger.detour_tolerance:
                continue

            if deviation < min_deviation:
                min_deviation = deviation
                best_pool = pool

        else:
            best_pool = pool

    if best_pool:
        passenger.ride_pool_id = best_pool.id
        return best_pool

    vehicle_result = await db.execute(select(Vehicle))
    vehicle = vehicle_result.scalars().first()

    new_pool = RidePool(vehicle_id=vehicle.id, status=PoolStatus.ACTIVE)
    db.add(new_pool)
    await db.flush()

    passenger.ride_pool_id = new_pool.id

    return new_pool
