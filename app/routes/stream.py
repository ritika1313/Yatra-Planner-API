from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from app.model import TravelRequestModel
from fastapi.responses import StreamingResponse
import json
from app.services.currency import fetch_currency_rates
from app.services.places import fetch_places
from app.services.weather import fetch_weather


router = APIRouter(
    prefix="/stream",
    tags=["Stream"],
)

def format_sse(data: object, event: str | None = None) -> str:
    json_data = json.dumps(jsonable_encoder(data))
    event_line = f"event: {event}\n" if event is not None else ""
    return f"{event_line}data: {json_data}\n\n"


async def stream_generator(travel_request: TravelRequestModel):
    yield format_sse({"message": "Starting travel plan aggregation.."}, event="start")
    yield format_sse({"message": "Fetching weather data..."}, event="weather")
    weather_data = await fetch_weather(
        destination=travel_request.destination,
        start_date=travel_request.start_date,
        end_date=travel_request.end_date,
    )

    yield format_sse({"weather_data": weather_data}, event="weather_complete")
    yield format_sse({"message": "Fetching travel options..."}, event="options")
    places_data = await fetch_places(travel_request.destination)
    yield format_sse({"places_data": places_data}, event="options_complete")

    yield format_sse({"message": "Fetching currency data...."}, event="currency")
    currency_data = await fetch_currency_rates(travel_request.base_currency)
    yield format_sse({"currency_data": currency_data}, event="currency_complete")
    yield format_sse({"message": "Travel plan aggregation complete!"}, event="complete")

@router.post("/post",response_class=StreamingResponse)
async def stream_travel_plan(travel_request: TravelRequestModel):
    if travel_request.start_date > travel_request.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date",
        )
    
    trip_days = (travel_request.end_date - travel_request.start_date).days
    
    if trip_days < 1:
        raise HTTPException(
            status_code=400,
            detail="Travel plan must be at least 1 day long",
        )
    
    if trip_days + 1 > 14:
        raise HTTPException(
            status_code=400,
            detail="Travel plan cannot be longer than 14 days",
        )

    return StreamingResponse(
        stream_generator(travel_request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )