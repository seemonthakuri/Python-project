"""Turns raw Outage records into a chart image for the dashboard.

Kept separate from models.py: models.py describes the data, this file
decides how to summarize and draw it.
"""

import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")  # no display available on a server - render to file only
import matplotlib.pyplot as plt
import pandas as pd


def build_outage_chart(outages):
    """Build a bar chart of total outage duration per day.

    outages: any iterable of Outage objects (ongoing ones are ignored,
             since they have no end_time yet to compute a duration from).

    Returns a base64-encoded PNG string ready to drop into an <img> tag,
    or None if there isn't any resolved data yet.
    """
    resolved = [o for o in outages if o.end_time is not None]
    if not resolved:
        return None

    df = pd.DataFrame({
        "date": [o.start_time.date() for o in resolved],
        "duration_hours": [o.duration_seconds / 3600 for o in resolved],
    })

    daily = df.groupby("date")["duration_hours"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(7, 3.2))
   

    ax.bar(daily.index.astype(str), daily.values, color="#1B3F62")
    ax.set_ylabel("Hours without power", color="#D4CFC9", fontweight="bold")
    ax.set_title("Outage duration by day", color="#D4CFC9", fontweight="bold")
    ax.tick_params(axis="x", rotation=45, colors="white")
    ax.tick_params(axis="y", colors="white")
    for spine in ax.spines.values():
        spine.set_color("white")
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=110, transparent=True)

    plt.close(fig)  # free the figure - matters if the app stays running
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")
