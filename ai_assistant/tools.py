from random import randint
from datetime import date, datetime, time
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from ai_assistant.rags import TravelGuideRAG
from ai_assistant.prompts import travel_guide_qa_tpl, travel_guide_description
from ai_assistant.config import get_agent_settings
from ai_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
)
from ai_assistant.utils import save_reservation
import wikipediaapi
import json
from typing import List

SETTINGS = get_agent_settings()

travel_guide_tool = QueryEngineTool(
    query_engine=TravelGuideRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=travel_guide_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=travel_guide_description, return_direct=False
    ),
)


# Tool functions
def reserve_flight(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Realiza una reserva de vuelo una fecha especifica de una ciudad a otra ciudad
    """
    print(
        f"Making flight reservation from {departure} to {destination} on date: {date}"
    )
    reservation = TripReservation(
        trip_type=TripType.flight,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(200, 700),
    )

    save_reservation(reservation)
    return reservation

def reserve_bus(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    Realiza una reserva de bus una fecha especifica de una ciudad a otra ciudad
    """
    print(f"Making bus reservation from {departure} to {destination} on date: {date_str}")
    reservation = TripReservation(
        trip_type=TripType.bus,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(50, 200),
    )
    save_reservation(reservation)
    return reservation

def reserve_hotel(checkin_date: str, checkout_date: str, hotel_name: str, city: str) -> HotelReservation:
    """
    Realiza una reserva de un hotel con una fecha especifica de checkin y checkout de un hotel en una ciudad especifica
    """
    print(f"Making hotel reservation at {hotel_name} in {city} from {checkin_date} to {checkout_date}")
    reservation = HotelReservation(
        checkin_date=date.fromisoformat(checkin_date),
        checkout_date=date.fromisoformat(checkout_date),
        hotel_name=hotel_name,
        city=city,
        cost=randint(500, 1500),
    )
    save_reservation(reservation)
    return reservation

def reserve_restaurant(reservation_time: str, restaurant: str, city: str, dish: str = "not specified") -> RestaurantReservation:
    """
    Realiza una reserva de un restaurante a una hora especifica de una ciudad
    """
    print(f"Making restaurant reservation at {restaurant} in {city} for {reservation_time}")
    reservation = RestaurantReservation(
        reservation_time=datetime.fromisoformat(reservation_time),
        restaurant=restaurant,
        city=city,
        dish=dish,
        cost=randint(20, 100),
    )
    save_reservation(reservation)
    return reservation

def trip_summary() -> str:
    with open(SETTINGS.log_file, "r") as file:
        trip_data = json.load(file)

    activities_by_city = {}
    total_cost = 0

    for activity in trip_data:
        city = activity.get('city', activity.get('departure', 'unknown'))
        date = activity.get('date', activity.get('checkin_date', 'unknown'))
        cost = activity.get('cost', 0)
        total_cost += cost

        if city not in activities_by_city:
            activities_by_city[city] = []

        activities_by_city[city].append({
            'activity': activity.get('reservation_type', 'Actividad'),
            'date': date,
            'details': activity,
        })

    summary = "Trip Summary:\n\n"
    for city, activities in activities_by_city.items():
        summary += f"City: {city}\n"
        for activity in activities:
            summary += f"  - Activity: {activity['activity']}\n"
            summary += f"    Date: {activity['date']}\n"
            summary += f"    Details: {json.dumps(activity['details'], indent=2)}\n"
        summary += "\n"

    summary += f"Total Cost: ${total_cost:.2f}\n"

    return summary

def get_wikipedia_page(lookup_term: str) -> str:
    user_agent = 'SegundoParcial/1.0 (https://www.upb.edu/)'
    wiki_wiki = wikipediaapi.Wikipedia('es')
    page = wiki_wiki.page(lookup_term)
    
    if page.exists():
        return page.text
    else:
        return f"No Wikipedia page found for {lookup_term}."


wikipedia_tool = FunctionTool.from_defaults(fn=get_wikipedia_page, return_direct=False)

trip_summary_tool = FunctionTool.from_defaults(fn=trip_summary, return_direct=False)

restaurant_tool = FunctionTool.from_defaults(fn=reserve_restaurant, return_direct=False)

hotel_tool = FunctionTool.from_defaults(fn=reserve_hotel, return_direct=False)

bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=False)

flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=False)
