import os
import json
import fitbit
import pandas as pd
from datetime import date, timedelta
from gather_keys_oauth2 import OAuth2Server

# ==== ENTER YOUR INFO HERE ====
CLIENT_ID = "23QM2Z"
CLIENT_SECRET = "1c49d9bcf0f24f1a6190e5a65f35021e"
REDIRECT_URI = "http://127.0.0.1:8080/"
TOKEN_FILE = "fitbit_tokens.json"

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

# ==== AUTHENTICATION ====
tokens = load_tokens()
if not tokens:
    server = OAuth2Server(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)
    server.browser_authorize()
    tokens = {
        "access_token": server.fitbit.client.session.token['access_token'],
        "refresh_token": server.fitbit.client.session.token['refresh_token']
    }
    save_tokens(tokens)

authd_client = fitbit.Fitbit(
    CLIENT_ID,
    CLIENT_SECRET,
    oauth2=True,
    access_token=tokens['access_token'],
    refresh_token=tokens['refresh_token']
)

# ==== DATE RANGE ====
end_date = date.today()
start_date = end_date - timedelta(days=30)  # last 30 days

# ==== METRICS TO DOWNLOAD ====
metrics = {
    "steps": "activities/steps",
    "calories": "activities/calories",
    "distance": "activities/distance",
    "floors": "activities/floors",
    "minutesSedentary": "activities/minutesSedentary",
    "minutesLightlyActive": "activities/minutesLightlyActive",
    "minutesFairlyActive": "activities/minutesFairlyActive",
    "minutesVeryActive": "activities/minutesVeryActive",
    "restingHeartRate": "activities/heart"
}

# ==== FETCH DATA ====
all_data = {}

for label, resource in metrics.items():
    print(f"Fetching {label}...")
    data = authd_client.time_series(
        resource,
        base_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    # Flatten JSON response
    key = list(data.keys())[0]
    df = pd.DataFrame(data[key])
    df.rename(columns={"value": label, "dateTime": "date"}, inplace=True)
    all_data[label] = df

# Merge all metrics into one DataFrame
df_final = None
for label, df in all_data.items():
    if df_final is None:
        df_final = df
    else:
        df_final = pd.merge(df_final, df, on="date", how="outer")

# Save to CSV
df_final.to_csv("fitbit_last30days.csv", index=False)
print("\n✅ Data saved to fitbit_last30days.csv")

print("\nPreview:\n", df_final.head())
