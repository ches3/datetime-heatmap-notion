import datetime
import math
import os
import sys

import matplotlib.pyplot as plt
import matplotlib_fontja  # noqa: F401
import pandas as pd
import requests
import seaborn as sns
from dotenv import load_dotenv

# Date range for filtering Notion data
start_date = "2024-01-01"
end_date = "2024-12-31"

# Column name of the date in Notion
column_name = "日時"

# Time range for the heatmap
start_time = 8
end_time = 24


load_dotenv()
notion_api_key = os.getenv("NOTION_API_KEY")
if not notion_api_key:
    print("Please set NOTION_API_KEY")
    sys.exit(1)
database_id = os.getenv("DATABASE_ID")
if not database_id:
    print("Please set DATABASE_ID")
    sys.exit(1)


# Fetch data from Notion
endpoint = f"https://api.notion.com/v1/databases/{database_id}/query"
headers = {
    "Notion-Version": "2022-06-28",
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
}

dt_list = []
cursor = None
while True:
    data = {
        "filter": {
            "and": [
                {
                    "property": column_name,
                    "date": {
                        "on_or_after": start_date,
                    },
                },
                {
                    "property": column_name,
                    "date": {
                        "on_or_before": end_date,
                    },
                },
            ]
        },
    }
    if cursor:
        data["start_cursor"] = cursor
    res = requests.post(endpoint, headers=headers, json=data)
    if not res.ok:
        print(res.text)
        sys.exit(1)
    res_json = res.json()

    for result in res_json["results"]:
        dt_list.append(result["properties"][column_name]["date"]["start"])

    if not res_json["has_more"]:
        break
    cursor = res_json["next_cursor"]


# Create DataFrame
count = [[0 for _ in range(7)] for _ in range(12)]

for dt_str in dt_list:
    dt = datetime.datetime.fromisoformat(dt_str)
    time_index = math.floor(dt.hour / 2)
    if time_index < 0:
        continue
    weekday_index = (dt.weekday() + 1) % 7
    count[time_index][weekday_index] += 1

index_label = [f"{i * 2}時" for i in range(12)]
columns_label = ["日", "月", "火", "水", "木", "金", "土"]

df = pd.DataFrame(count, index=index_label, columns=columns_label)


# Plot heatmap
start_time_index = math.floor(start_time / 2)
end_time_index = math.floor(end_time / 2)

sns.heatmap(
    df.iloc[start_time_index:end_time_index],
    cmap="Oranges",
    linewidths=1,
    linecolor="white",
    square=True,
    cbar_kws={"ticks": range(0, df.values.max() + 1)},
)
plt.tick_params(axis="y", labelrotation=0)
plt.show()
