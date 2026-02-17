def calculate_price(distance_km, passenger_count, luggage):

    base_rate = 12
    base_price = distance_km * base_rate

    demand_multiplier = 1.2 if passenger_count >= 3 else 1
    sharing_discount = 0.15 * (passenger_count - 1)
    luggage_fee = 30 if luggage > 2 else 0

    final_price = base_price * demand_multiplier * (1 - sharing_discount)
    final_price += luggage_fee

    return round(final_price, 2)
