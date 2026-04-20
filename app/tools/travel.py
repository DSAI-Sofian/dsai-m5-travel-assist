import os
import httpx
from amadeus import Client


def amadeus_client():
    return Client(
        client_id=os.getenv("AMADEUS_CLIENT_ID", ""),
        client_secret=os.getenv("AMADEUS_CLIENT_SECRET", "")
    )


def airport_code_lookup(keyword: str):
    amadeus = amadeus_client()
    return amadeus.reference_data.locations.get(keyword=keyword, subType="AIRPORT,CITY").data


def flight_offers(origin: str, destination: str, depart_date: str, adults: int = 1):
    amadeus = amadeus_client()
    return amadeus.shopping.flight_offers_search.get(
        originLocationCode=origin,
        destinationLocationCode=destination,
        departureDate=depart_date,
        adults=adults
    ).data


def hotel_offers(city_code: str, adults: int = 1):
    amadeus = amadeus_client()
    return amadeus.shopping.hotel_offers_search.get(cityCode=city_code, adults=adults).data


def activities(lat: float, lon: float, radius_km: int = 20):
    amadeus = amadeus_client()
    return amadeus.shopping.activities.get(latitude=lat, longitude=lon, radius=radius_km).data


def rome2rio_search(origin: str, destination: str):
    api_key = os.getenv("ROME2RIO_API_KEY", "")
    if not api_key:
        return {"error": "ROME2RIO_API_KEY missing"}
    url = "https://api.rome2rio.com/api/1.4/json/Search"
    params = {"key": api_key, "oName": origin, "dName": destination}
    r = httpx.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()
