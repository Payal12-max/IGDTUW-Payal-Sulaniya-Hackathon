import urllib.parse
import urllib.request
import pandas as pd
from io import StringIO

query = "financial markets"

params = {
    "query": query,
    "mode": "artlist",
    "format": "csv",
    "maxrecords": 10,
    "timespan": "1d",
    "sort": "datedesc",
}

url = (
    "https://api.gdeltproject.org/api/v2/doc/doc?"
    + urllib.parse.urlencode(params)
)

print("Requesting GDELT data...")

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "RiskPulse-Hackathon-Prototype/1.0"
    },
)

with urllib.request.urlopen(request, timeout=30) as response:
    csv_data = response.read().decode("utf-8")

df = pd.read_csv(StringIO(csv_data))

print("\nColumns:")
print(df.columns.tolist())

print(f"\nRows: {len(df)}")

print("\nSample:")
print(df.head(10).to_string(index=False))