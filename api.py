import os
import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd
from datetime import date

# ==== ENTER YOUR INFO HERE ====
CLIENT_ID = "23QM2Z"
CLIENT_SECRET = "1c49d9bcf0f24f1a6190e5a65f35021e"
REDIRECT_URI = "http://127.0.0.1:8080/"  # Must match your Fitbit app settings

# ==== AUTHENTICATION ====
server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET, redirect_uri=REDIRECT_URI)
server.browser_authorize()

ACCESS_TOKEN = str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN = str(server.fitbit.client.session.token['refresh_token'])

print("Access Token:", ACCESS_TOKEN)
print("Refresh Token:", REFRESH_TOKEN)

authd_client = fitbit.Fitbit(
    CLIENT_ID,
    CLIENT_SECRET,
    oauth2=True,
    access_token=ACCESS_TOKEN,
    refresh_token=REFRESH_TOKEN
)

# ==== EXAMPLE DATA FETCH ====
# Daily steps
today = date.today().isoformat()  # e.g., "2025-08-25"
fit_stats_steps = authd_client.activities(date=today)
print("\nToday's Steps:", fit_stats_steps["summary"]["steps"])

# Resting heart rate
fit_stats_heart = authd_client.time_series("activities/heart", base_date=today, period="1d")
print("\nResting Heart Rate Data:", fit_stats_heart)
