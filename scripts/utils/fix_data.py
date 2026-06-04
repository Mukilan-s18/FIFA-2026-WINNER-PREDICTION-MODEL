import pandas as pd
import json

preds = pd.read_csv('reports/tournament_predictions.csv')
squads = pd.read_csv('data/raw/squad_values.csv')

# Merge on team name
merged = pd.merge(preds, squads, left_on='team', right_on='team_name', how='left')

data = []
for _, row in merged.iterrows():
    data.append({
        'team': row['team'],
        'win_prob': float(row['win_prob']),
        'final_prob': float(row['final_prob']),
        'semi_prob': float(row['semi_prob']),
        'group_win_prob': float(row.get('group_win_prob', 0.5)),
        'ro16_prob': float(row.get('ro16_prob', 0.4)),
        'quarter_prob': float(row.get('quarter_prob', 0.2)),
        'squad_value_m': float(row.get('squad_value_m', 10.0)),
        'fifa_rating': float(row.get('fifa_rating', 70.0))
    })

with open('web_app/public/data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Restored squad_value_m to data.json")
