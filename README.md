# Country Data Pipeline & Analytics

This capstone scrapes the first 20 country cards from Scrape This Site, stores them in SQLite with `country_name` as the natural primary key, serves CRUD operations through FastAPI, and exports API data to CSV and a scatter plot.

## Project files

- `scraper.py` — fetches and parses the first 20 source-page cards, then inserts or refreshes them in the database.
- `database.py` — SQLite schema and object-oriented CRUD manager.
- `main.py` — FastAPI REST API.
- `client.py` — downloads API records into a Pandas DataFrame, prints it, exports CSV, and saves the plot.
- `countries.db` — created by the scraper.
- `exported_countries.csv`, `population_vs_area.png` — created by the client.

## Setup and run

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scraper.py
uvicorn main:app --reload
```

In a second PowerShell window, activate the same environment and run:

```powershell
python client.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scraper.py
uvicorn main:app --reload
```

In another terminal, activate the environment and run `python client.py`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs` while the server is running.

## Endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/countries` | List all stored countries |
| GET | `/countries/{country_name}` | Get one country by its full name |
| POST | `/countries` | Create a record; returns 409 if the natural key exists |
| PUT | `/countries/{country_name}` | Replace the record fields; path and body names must match |
| DELETE | `/countries/{country_name}` | Delete a record; returns 404 if it does not exist |

The scatter plot uses a symmetric logarithmic population axis and a logarithmic area axis so Antarctica's zero population and the large differences in scale remain visible.
