"""FastAPI service exposing country CRUD operations."""

from contextlib import contextmanager
from typing import Iterator

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

from database import CountryDatabaseManager

app = FastAPI(title="Country Data API", version="1.0.0")


class CountryPayload(BaseModel):
    country_name: str = Field(min_length=1, max_length=120)
    capital: str = Field(max_length=120)
    population: int = Field(ge=0)
    area: float = Field(ge=0)


@contextmanager
def database() -> Iterator[CountryDatabaseManager]:
    manager = CountryDatabaseManager()
    try:
        yield manager
    finally:
        manager.close()


@app.get("/countries", response_model=list[CountryPayload])
def list_countries() -> list[dict]:
    with database() as manager:
        return manager.get_all_countries()


@app.get("/countries/{country_name}", response_model=CountryPayload)
def get_country(country_name: str) -> dict:
    with database() as manager:
        country = manager.get_country(country_name)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@app.post("/countries", response_model=CountryPayload, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryPayload) -> dict:
    with database() as manager:
        if manager.get_country(payload.country_name):
            raise HTTPException(status_code=409, detail="Country already exists")
        return manager.create_country(**payload.model_dump())


@app.put("/countries/{country_name}", response_model=CountryPayload)
def update_country(country_name: str, payload: CountryPayload) -> dict:
    if payload.country_name != country_name:
        raise HTTPException(status_code=422, detail="Path and body country_name must match")
    with database() as manager:
        updated = manager.update_country(
            country_name, payload.capital, payload.population, payload.area
        )
    if updated is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return updated


@app.delete("/countries/{country_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_name: str) -> Response:
    with database() as manager:
        deleted = manager.delete_country(country_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Country not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
