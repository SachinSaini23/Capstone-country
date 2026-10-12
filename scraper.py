"""Scrape the first 20 country records from Scrape This Site."""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from database import CountryDatabaseManager

SOURCE_URL = "https://www.scrapethissite.com/pages/simple/"
COUNTRY_LIMIT = 20


def scrape_countries(limit: int = COUNTRY_LIMIT) -> list[dict]:
    """Fetch and parse country cards in their source-page order."""
    response = requests.get(
        SOURCE_URL,
        timeout=30,
        headers={"User-Agent": "CountryDataCapstone/1.0 (educational project)"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    countries = []
    for card in soup.select("div.country")[:limit]:
        name = card.select_one("h3.country-name")
        capital = card.select_one("span.country-capital")
        population = card.select_one("span.country-population")
        area = card.select_one("span.country-area")
        if not all((name, capital, population, area)):
            raise ValueError("A country card is missing one or more expected fields")

        population_value = int(re.sub(r"[^0-9]", "", population.get_text(" ", strip=True)))
        area_value = float(area.get_text(" ", strip=True).replace(",", ""))
        capital_value = capital.get_text(" ", strip=True)
        countries.append(
            {
                "country_name": name.get_text(" ", strip=True),
                "capital": "" if capital_value.lower() == "none" else capital_value,
                "population": population_value,
                "area": area_value,
            }
        )

    if len(countries) != min(limit, 20):
        raise ValueError(f"Expected {min(limit, 20)} countries, found {len(countries)}")
    return countries


def refresh_database() -> int:
    """Scrape the source and insert or update the local SQLite records."""
    countries = scrape_countries()
    with CountryDatabaseManager() as database:
        for country in countries:
            database.upsert_country(**country)
    return len(countries)


if __name__ == "__main__":
    count = refresh_database()
    print(f"Scraped and saved {count} countries to countries.db")
