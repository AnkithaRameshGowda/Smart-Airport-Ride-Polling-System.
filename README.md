**Smart Airport Ride Pooling Backend**

## Tech Stack:
    FastAPI (Async)
    PostgreSQL
    SQLAlchemy (Async ORM)
    Uvicorn

## Functional Requirements Implemented

    Group passengers into shared cabs
    Seat constraint validation
    Luggage constraint validation
    Minimize total travel deviation (Haversine distance)
    Enforce detour tolerance
    Real-time cancellation
    Dynamic pricing engine
    Concurrency handling using row-level locking

## High-Level Architecture

Client → FastAPI → Matching Engine → Pricing Engine → PostgreSQL

    FastAPI handles REST APIs
    Matching Engine selects optimal ride pool
    Pricing Engine computes dynamic fare
    PostgreSQL ensures transactional safety

## Database Schema
    vehicles:
    id (PK)
    total_seats
    luggage_capacity

    ride_pools:
    id (PK)
    vehicle_id (FK)
    status (ACTIVE/FULL/CANCELLED)

    passengers:
    id (PK)
    ride_pool_id (FK)
    luggage
    seats_required
    source/destination coordinates
    detour_tolerance

    Indexes:
    ride_pools.status
    passengers.ride_pool_id

## Matching Algorithm

For each incoming passenger:
    1.Fetch ACTIVE ride pools (with row lock)
    2.Validate seat and luggage capacity
    3.Calculate deviation using Haversine formula
    4.Select pool with minimum deviation
    5.If no valid pool, create new pool

Time Complexity:
O(n) per request (n = active pools)

## Concurrency Handling

Used SELECT ... FOR UPDATE
Row-level locking prevents race conditions
Ensures no seat overbooking

## Dynamic Pricing Formula
$$
final_price =(base_rate × distance) × demand_multiplier × (1 - sharing_discount) + luggage_fee
$$

## Performance Considerations
    Async FastAPI
    Connection pooling
    Indexed columns
    O(n) matching
    Designed to handle 100 requests/sec
    Low latency DB queries

## Running the Project

1.Install PostgreSQL

2.Create database ride_pooling_db

3.Insert vehicle:

```sql
INSERT INTO vehicles (total_seats, luggage_capacity)
VALUES (4, 6);
```

4.Install dependencies:

```bash
pip install -r requirements.txt
```

5.Run server:

```bash
uvicorn app.main:app --reload
```

6.Open:

```browser
http://127.0.0.1:8000/docs
```