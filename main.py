from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import engine, Base, AsyncSessionLocal
from app import models, schemas
from app.matching import match_passenger
from app.pricing import calculate_price


app = FastAPI(title="Smart Airport Ride Pooling Backend")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/request-ride")
async def request_ride(
    passenger: schemas.PassengerCreate,
    db: AsyncSession = Depends(get_db)
):

    db_passenger = models.Passenger(**passenger.model_dump())
    db.add(db_passenger)
    await db.flush()

    pool = await match_passenger(db, db_passenger)

    await db.commit()

    result = await db.execute(
        select(func.count(models.Passenger.id))
        .where(models.Passenger.ride_pool_id == pool.id)
    )
    passenger_count = result.scalar()

    price = calculate_price(20, passenger_count, passenger.luggage)

    return {
        "message": "Ride assigned",
        "pool_id": pool.id,
        "price": price
    }


@app.post("/cancel-ride/{passenger_id}")
async def cancel_ride(passenger_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.Passenger).where(models.Passenger.id == passenger_id)
    )
    passenger = result.scalar_one_or_none()

    if not passenger:
        return {"error": "Passenger not found"}

    passenger.ride_pool_id = None
    await db.commit()

    return {"message": "Ride cancelled"}
