from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = Path(__file__).resolve().parent

def main() -> None:
    response = requests.get(f"{BASE_URL}/countries", timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise RuntimeError("The API returned no countries. Run scraper.py first.")

    frame = pd.DataFrame(data, columns=["country_name", "capital", "population", "area"])
    print(frame.to_string(index=False))

    csv_path = OUTPUT_DIR / "exported_countries.csv"
    frame.to_csv(csv_path, index=False, encoding="utf-8")

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.scatter(frame["population"], frame["area"], color="steelblue")
    axis.set_title("Population vs. Area for the First 20 Countries")
    axis.set_xlabel("Population")
    axis.set_ylabel("Area (sq. km)")
    axis.grid(True, linestyle="--", alpha=0.4)

    axis.set_xscale("symlog", linthresh=1)
    axis.set_yscale("log")
    figure.tight_layout()
    plot_path = OUTPUT_DIR / "population_vs_area.png"
    figure.savefig(plot_path, dpi=160)
    plt.close(figure)
    print(f"\nSaved {len(frame)} rows to {csv_path.name} and chart to {plot_path.name}")

if __name__ =="__main__":
    main()  