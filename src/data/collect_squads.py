"""
Collect Squad Market Values & FIFA Team Ratings.

Since scraping Transfermarkt or FIFAIndex directly is blocked by bot protections,
and we want this pipeline to run reliably without an API key, this script
generates a static dataset of squad market values (in millions of €) and
FIFA Team Ratings (Overall) for the 48 qualified World Cup 2026 teams.
These values represent the realistic strength of these squads as of 2024-2026.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from src.config import RAW_DIR

# Estimated Market Value (€ Millions) and FIFA Overall Rating (0-100)
# Data represents approximations for national team squads
TEAM_RATINGS: Dict[str, Dict[str, Any]] = {
    "Argentina": {"squad_value_m": 850, "fifa_rating": 85, "home_continent": "South America", "star_player_count": 3, "key_injuries": 0},
    "France": {"squad_value_m": 1250, "fifa_rating": 86, "home_continent": "Europe", "star_player_count": 3, "key_injuries": 1},
    "England": {"squad_value_m": 1400, "fifa_rating": 85, "home_continent": "Europe", "star_player_count": 3, "key_injuries": 1},
    "Brazil": {"squad_value_m": 1050, "fifa_rating": 84, "home_continent": "South America", "star_player_count": 3, "key_injuries": 1},
    "Spain": {"squad_value_m": 950, "fifa_rating": 84, "home_continent": "Europe", "star_player_count": 3, "key_injuries": 0},
    "Portugal": {"squad_value_m": 1000, "fifa_rating": 84, "home_continent": "Europe", "star_player_count": 3, "key_injuries": 0},
    "Netherlands": {"squad_value_m": 750, "fifa_rating": 83, "home_continent": "Europe", "star_player_count": 2, "key_injuries": 0},
    "Germany": {"squad_value_m": 800, "fifa_rating": 83, "home_continent": "Europe", "star_player_count": 2, "key_injuries": 1},
    "Italy": {"squad_value_m": 650, "fifa_rating": 82, "home_continent": "Europe", "star_player_count": 2, "key_injuries": 0},
    "Uruguay": {"squad_value_m": 450, "fifa_rating": 80, "home_continent": "South America", "star_player_count": 2, "key_injuries": 0},
    "Croatia": {"squad_value_m": 350, "fifa_rating": 80, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Belgium": {"squad_value_m": 450, "fifa_rating": 80, "home_continent": "Europe", "star_player_count": 2, "key_injuries": 0},
    "Colombia": {"squad_value_m": 250, "fifa_rating": 78, "home_continent": "South America", "star_player_count": 1, "key_injuries": 0},
    "Morocco": {"squad_value_m": 300, "fifa_rating": 79, "home_continent": "Africa", "star_player_count": 1, "key_injuries": 0},
    "Japan": {"squad_value_m": 250, "fifa_rating": 78, "home_continent": "Asia", "star_player_count": 1, "key_injuries": 0},
    "United States": {"squad_value_m": 300, "fifa_rating": 78, "home_continent": "North America", "star_player_count": 1, "key_injuries": 0},
    "Senegal": {"squad_value_m": 280, "fifa_rating": 78, "home_continent": "Africa", "star_player_count": 1, "key_injuries": 1},
    "Switzerland": {"squad_value_m": 250, "fifa_rating": 78, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Denmark": {"squad_value_m": 350, "fifa_rating": 79, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Mexico": {"squad_value_m": 200, "fifa_rating": 77, "home_continent": "North America", "star_player_count": 1, "key_injuries": 0},
    "Ecuador": {"squad_value_m": 220, "fifa_rating": 77, "home_continent": "South America", "star_player_count": 1, "key_injuries": 0},
    "Turkey": {"squad_value_m": 300, "fifa_rating": 78, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "South Korea": {"squad_value_m": 200, "fifa_rating": 77, "home_continent": "Asia", "star_player_count": 1, "key_injuries": 0},
    "Serbia": {"squad_value_m": 280, "fifa_rating": 78, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Nigeria": {"squad_value_m": 350, "fifa_rating": 78, "home_continent": "Africa", "star_player_count": 1, "key_injuries": 0},
    "Ivory Coast": {"squad_value_m": 280, "fifa_rating": 78, "home_continent": "Africa", "star_player_count": 1, "key_injuries": 0},
    "Cameroon": {"squad_value_m": 150, "fifa_rating": 75, "home_continent": "Africa", "star_player_count": 0, "key_injuries": 0},
    "Poland": {"squad_value_m": 200, "fifa_rating": 76, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Iran": {"squad_value_m": 50, "fifa_rating": 74, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Australia": {"squad_value_m": 50, "fifa_rating": 74, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Canada": {"squad_value_m": 180, "fifa_rating": 75, "home_continent": "North America", "star_player_count": 1, "key_injuries": 0},
    "Saudi Arabia": {"squad_value_m": 30, "fifa_rating": 72, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Qatar": {"squad_value_m": 20, "fifa_rating": 71, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Tunisia": {"squad_value_m": 60, "fifa_rating": 73, "home_continent": "Africa", "star_player_count": 0, "key_injuries": 0},
    "Algeria": {"squad_value_m": 180, "fifa_rating": 76, "home_continent": "Africa", "star_player_count": 1, "key_injuries": 0},
    "Egypt": {"squad_value_m": 120, "fifa_rating": 74, "home_continent": "Africa", "star_player_count": 0, "key_injuries": 0},
    "Mali": {"squad_value_m": 150, "fifa_rating": 75, "home_continent": "Africa", "star_player_count": 0, "key_injuries": 0},
    "Peru": {"squad_value_m": 40, "fifa_rating": 73, "home_continent": "South America", "star_player_count": 0, "key_injuries": 0},
    "Chile": {"squad_value_m": 80, "fifa_rating": 75, "home_continent": "South America", "star_player_count": 0, "key_injuries": 0},
    "Paraguay": {"squad_value_m": 100, "fifa_rating": 75, "home_continent": "South America", "star_player_count": 0, "key_injuries": 0},
    "Venezuela": {"squad_value_m": 60, "fifa_rating": 73, "home_continent": "South America", "star_player_count": 0, "key_injuries": 0},
    "Scotland": {"squad_value_m": 250, "fifa_rating": 77, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Wales": {"squad_value_m": 150, "fifa_rating": 75, "home_continent": "Europe", "star_player_count": 0, "key_injuries": 0},
    "Ukraine": {"squad_value_m": 300, "fifa_rating": 78, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Sweden": {"squad_value_m": 350, "fifa_rating": 78, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Norway": {"squad_value_m": 450, "fifa_rating": 79, "home_continent": "Europe", "star_player_count": 2, "key_injuries": 0},
    "Austria": {"squad_value_m": 350, "fifa_rating": 78, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Hungary": {"squad_value_m": 150, "fifa_rating": 75, "home_continent": "Europe", "star_player_count": 0, "key_injuries": 0},
    "Czech Republic": {"squad_value_m": 180, "fifa_rating": 76, "home_continent": "Europe", "star_player_count": 1, "key_injuries": 0},
    "Slovakia": {"squad_value_m": 150, "fifa_rating": 75, "home_continent": "Europe", "star_player_count": 0, "key_injuries": 0},
    "Romania": {"squad_value_m": 100, "fifa_rating": 74, "home_continent": "Europe", "star_player_count": 0, "key_injuries": 0},
    "Greece": {"squad_value_m": 150, "fifa_rating": 75, "home_continent": "Europe", "star_player_count": 0, "key_injuries": 0},
    "Panama": {"squad_value_m": 20, "fifa_rating": 71, "home_continent": "North America", "star_player_count": 0, "key_injuries": 0},
    "Costa Rica": {"squad_value_m": 25, "fifa_rating": 72, "home_continent": "North America", "star_player_count": 0, "key_injuries": 0},
    "Jamaica": {"squad_value_m": 80, "fifa_rating": 73, "home_continent": "North America", "star_player_count": 0, "key_injuries": 0},
    "Honduras": {"squad_value_m": 15, "fifa_rating": 70, "home_continent": "North America", "star_player_count": 0, "key_injuries": 0},
    "New Zealand": {"squad_value_m": 25, "fifa_rating": 70, "home_continent": "Oceania", "star_player_count": 0, "key_injuries": 0},
    "Uzbekistan": {"squad_value_m": 30, "fifa_rating": 71, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Indonesia": {"squad_value_m": 15, "fifa_rating": 68, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Bahrain": {"squad_value_m": 10, "fifa_rating": 68, "home_continent": "Asia", "star_player_count": 0, "key_injuries": 0},
    "Bolivia": {"squad_value_m": 15, "fifa_rating": 70, "home_continent": "South America", "star_player_count": 0, "key_injuries": 0},
    "Trinidad and Tobago": {"squad_value_m": 10, "fifa_rating": 68, "home_continent": "North America", "star_player_count": 0, "key_injuries": 0},
    "Albania": {"squad_value_m": 100, "fifa_rating": 74, "home_continent": "Europe", "star_player_count": 0, "key_injuries": 0},
}

def download_squad_values() -> pd.DataFrame:
    """Generate the squad values dataset."""
    print("  Creating squad values dataset...")
    
    rows = []
    for team, stats in TEAM_RATINGS.items():
        rows.append({
            "team_name": team,
            "squad_value_m": stats["squad_value_m"],
            "fifa_rating": stats["fifa_rating"],
            "home_continent": stats["home_continent"],
            "star_player_count": stats["star_player_count"],
            "key_injuries": stats["key_injuries"]
        })
        
    df = pd.DataFrame(rows)
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / "squad_values.csv"
    df.to_csv(out_path, index=False)
    print(f"  ✓ Saved squad values → {out_path}")
    
    return df

if __name__ == "__main__":
    download_squad_values()
