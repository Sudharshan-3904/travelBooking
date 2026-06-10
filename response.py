import os
import json
import hashlib

def get_data_path(filename):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(curr_dir, 'data', filename)
    if os.path.exists(path):
        return path
    return os.path.join('data', filename)

def deterministic_hash(val: str, min_val: int, max_val: int) -> int:
    h = hashlib.md5(val.encode('utf-8')).hexdigest()
    num = int(h, 16)
    return min_val + (num % (max_val - min_val + 1))

def query_flights(origin: str, destination: str, departure_date: str = None, return_date: str = None):
    flights_path = get_data_path('flights.json')
    if not os.path.exists(flights_path):
        return "No flights database found."
        
    try:
        with open(flights_path, 'r', encoding='utf-8') as f:
            flights = json.load(f)
    except Exception as e:
        return f"Error loading flights database: {e}"
        
    origin_clean = origin.strip().lower()
    dest_clean = destination.strip().lower()
    
    matched = []
    for flight in flights:
        orig_name = flight.get('airport', {}).get('name', '').lower()
        orig_code = flight.get('airport', {}).get('iataCode', '').lower()
        dest_name = flight.get('airport.2', {}).get('name', '').lower()
        dest_code = flight.get('airport.2', {}).get('iataCode', '').lower()
        
        orig_match = origin_clean in orig_name or origin_clean in orig_code
        dest_match = dest_clean in dest_name or dest_clean in dest_code
        
        if orig_match and dest_match:
            matched.append(flight)
            
    # Fallback: Find connecting/one-stop flights if no direct ones
    if not matched:
        origins_matching = [
            f for f in flights 
            if origin_clean in f.get('airport', {}).get('name', '').lower() 
            or origin_clean in f.get('airport', {}).get('iataCode', '').lower()
        ]
        dests_matching = [
            f for f in flights 
            if dest_clean in f.get('airport.2', {}).get('name', '').lower() 
            or dest_clean in f.get('airport.2', {}).get('iataCode', '').lower()
        ]
        
        for o_flight in origins_matching[:5]:
            for d_flight in dests_matching[:5]:
                matched.append({
                    'airline': o_flight['airline'],
                    'airplane': o_flight['airplane'],
                    'flightNumber': f"{o_flight['flightNumber']}/{d_flight['flightNumber']}",
                    'airport': o_flight['airport'],
                    'airport.2': d_flight['airport.2'],
                    'layover': o_flight['airport.2'],
                    'future': o_flight['future']
                })
                
    # If still no flights, simulate/adapt top 3 flights to match input
    if not matched:
        for flight in flights[:3]:
            matched.append({
                'airline': flight['airline'],
                'airplane': flight['airplane'],
                'flightNumber': flight['flightNumber'],
                'airport': {'name': f"{origin} International Airport", 'iataCode': origin[:3].upper()},
                'airport.2': {'name': f"{destination} International Airport", 'iataCode': destination[:3].upper()},
                'future': departure_date or flight['future']
            })
            
    formatted_results = []
    for f in matched[:5]:
        airline_name = f['airline']['name']
        iata = f['airline']['iataCode']
        flight_num = f['flightNumber']
        origin_airport = f['airport']['name']
        origin_code = f['airport']['iataCode']
        dest_airport = f['airport.2']['name']
        dest_code = f['airport.2']['iataCode']
        dep_time = f['future']
        
        price = deterministic_hash(f"{airline_name}{flight_num}", 250, 750)
        
        layover_str = ""
        if 'layover' in f:
            layover_str = f" (Layover at {f['layover']['name']} [{f['layover']['iataCode']}])"
            
        formatted_results.append(
            f"- {airline_name} ({iata} {flight_num}): {origin_airport} ({origin_code}) to {dest_airport} ({dest_code}){layover_str}\n"
            f"  Departure: {dep_time}\n"
            f"  Price: ${price} per traveler"
        )
        
    return "\n\n".join(formatted_results)

def query_hotels(destination: str):
    hotels_path = get_data_path('hotels.json')
    if not os.path.exists(hotels_path):
        return "No hotels database found."
        
    try:
        with open(hotels_path, 'r', encoding='utf-8') as f:
            hotels = json.load(f)
    except Exception as e:
        return f"Error loading hotels database: {e}"
        
    dest_clean = destination.strip().lower()
    
    matched = []
    for hotel in hotels:
        city = hotel.get('city', '').lower()
        state = hotel.get('state', '').lower()
        country = hotel.get('country', '').lower()
        
        if dest_clean in city or dest_clean in state or dest_clean in country:
            matched.append(hotel)
            
    # Fallback to top 5 hotels adapted to the requested destination
    if not matched:
        for hotel in hotels[:5]:
            adapted_hotel = hotel.copy()
            adapted_hotel['city'] = destination
            adapted_hotel['state'] = "State"
            adapted_hotel['country'] = "Country"
            matched.append(adapted_hotel)
            
    formatted_results = []
    for h in matched[:5]:
        name = h['fullName']
        phone = h['number']
        address = h['streetAddress']
        city = h['city']
        state = h['state']
        country = h['country']
        
        price_per_night = deterministic_hash(name, 80, 250)
        
        formatted_results.append(
            f"- {name} Resort & Hotel\n"
            f"  Address: {address}, {city}, {state}, {country}\n"
            f"  Phone: {phone}\n"
            f"  Price: ${price_per_night} per night"
        )
        
    return "\n\n".join(formatted_results)
