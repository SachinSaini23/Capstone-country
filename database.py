"""SQLite persistence layer for country records."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "countries.db"


class CountryDatabaseManager:
    """Owns SQLite connections and CRUD operations for countries."""

    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.db_path = str(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_table()

    def _create_table(self) -> None:
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS countries (
                country_name TEXT PRIMARY KEY,
                capital TEXT NOT NULL,
                population INTEGER NOT NULL CHECK (population >= 0),
                area REAL NOT NULL CHECK (area >= 0)
            )"""
        )
        self.connection.commit()

    @staticmethod
    def _as_dict(row: sqlite3.Row | None) -> dict | None:
        return dict(row) if row is not None else None

    def create_country(self, country_name: str, capital: str, population: int, area: float) -> dict:
        self.connection.execute(
            "INSERT INTO countries (country_name, capital, population, area) VALUES (?, ?, ?, ?)",
            (country_name, capital, population, area),
        )
        self.connection.commit()
        return self.get_country(country_name)  # type: ignore[return-value]

    def upsert_country(self, country_name: str, capital: str, population: int, area: float) -> dict:
        """Insert a scraped record or refresh its values using its natural key."""
        self.connection.execute(
            """INSERT INTO countries (country_name, capital, population, area)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(country_name) DO UPDATE SET
                 capital = excluded.capital,
                 population = excluded.population,
                 area = excluded.area""",
            (country_name, capital, population, area),
        )
        self.connection.commit()
        return self.get_country(country_name)  # type: ignore[return-value]

    def get_all_countries(self) -> list[dict]:
        rows = self.connection.execute(
            "SELECT country_name, capital, population, area FROM countries ORDER BY rowid"
        ).fetchall()
        return [dict(row) for row in rows]

    def get_country(self, country_name: str) -> dict | None:
        row = self.connection.execute(
            "SELECT country_name, capital, population, area FROM countries WHERE country_name = ?",
            (country_name,),
        ).fetchone()
        return self._as_dict(row)

    def update_country(self, country_name: str, capital: str, population: int, area: float) -> dict | None:
        cursor = self.connection.execute(
            "UPDATE countries SET capital = ?, population = ?, area = ? WHERE country_name = ?",
            (capital, population, area, country_name),
        )
        self.connection.commit()
        return self.get_country(country_name) if cursor.rowcount else None

    def delete_country(self, country_name: str) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM countries WHERE country_name = ?", (country_name,)
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "CountryDatabaseManager":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
