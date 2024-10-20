from fastapi import FastAPI, Depends, Query
from llama_index.core.agent import ReActAgent
from ai_assistant.agent import TravelAgent
from ai_assistant.models import AgentAPIResponse, RecommendationRequest, ReservationRequest, HotelReservationRequest,RestaurantReservationRequest
from typing import Optional, List
from ai_assistant.tools import (
    reserve_flight,
    reserve_bus,
    reserve_hotel,
    reserve_restaurant
)

app = FastAPI(title="AI Travel Agent API")

def get_agent() -> ReActAgent:
    return TravelAgent().get_agent()

@app.get("/recommendations/places")
def recommend_places(
    city: str,
    notes: Optional[List[str]] = Query(None),
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend places to visit in {city}."
    if notes:
        prompt += f" Consider these notes: {notes}."
    
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))

@app.get("/recommendations/hotels")
def recommend_hotels(
    city: str,
    notes: Optional[List[str]] = Query(None),
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend hotels to stay in {city}."
    if notes:
        prompt += f" Consider these notes: {notes}."
    
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))

@app.get("/recommendations/activities")
def recommend_activities(
    city: str,
    notes: Optional[List[str]] = Query(None),
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend activities to do in {city}."
    if notes:
        prompt += f" Consider these notes: {notes}."
    
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))


@app.post("/reservations/flight")
def reserve_flight_api(request: RecommendationRequest = Query(...)):
    reservation = reserve_flight(
        request.origin,
        request.destination,
        request.date)
    return {"status": "Flight reserved", "details": reservation.dict()}

@app.post("/reservations/bus")
def reserve_bus_api(request: ReservationRequest = Query(...)):
    reservation = reserve_bus(
        request.date,
        request.origin,
        request.destination)
    return {"status": "Bus ticket reserved", "details": reservation.dict()}

@app.post("/reservations/hotel")
def reserve_hotel_api(request: HotelReservationRequest = Query(...)):
    reservation = reserve_hotel(
        request.checkin_date,
        request.checkout_date,
        request.hotel, request.city)
    return {"status": "Hotel room reserved", "details": reservation.dict()}

@app.post("/reservations/restaurant")
def reserve_restaurant_api(request: RestaurantReservationRequest = Query(...)):

    if not request.dish:
        request.dish = "not specified"

    reservation = reserve_restaurant(
        f"{request.date}T{request.time}", 
        request.restaurant, 
        request.city, 
        request.dish
    )
    return {"status": "Restaurant table reserved", "details": reservation.dict()}

@app.get("/trip/report")
def generate_trip_report(agent: ReActAgent = Depends(get_agent)):
    prompt = f"""
        Generate a detailed trip report based on the log of activities. 
        Include all activities organized by place and date, a budget summary, and comments on the places and activities.

        Please generate a trip summary using the tool `trip_summary_tool`.
        
        The detailed report should include:
        1. Key highlights of the trip.
        2. Any identified recommendations.

        Use the `trip_summary_tool` to create the summary as the first step, then follow with the report.

        Please include both the trip summary and the detailed report in **Spanish** in your **final Answer**.
        Make sure to return both the summary and the detailed report as part of the final **Answer**, and not as internal thoughts or reasoning.
        """
    
    
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))

