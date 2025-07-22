import pandas as pd
import json
import math

# Load the edited Excel file
df = pd.read_excel("recorded_actions.xlsx")

# Replace pandas NaN with None for easier testing
df = df.where(pd.notnull(df), None)

# Build a list of clean action dicts
clean_actions = []
for record in df.to_dict(orient='records'):
    # Drop keys where the value is None or NaN
    filtered = {
        k: v
        for k, v in record.items()
        if v is not None and not (isinstance(v, float) and math.isnan(v))
    }
    clean_actions.append(filtered)

# Export to JSON
with open("recorded_actions_mod.json", "w") as f:
    json.dump(clean_actions, f, indent=4)

print("Modified actions saved to recorded_actions_mod.json (omitting null/NaN fields)")
