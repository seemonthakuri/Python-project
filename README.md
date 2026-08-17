# Load-Shedding Logger

A small Flask app for tracking power outages. When the power goes out you log it, when it comes back you mark it resolved, and the app works out how long it lasted on its own instead of you having to type it in. Data's stored in PostgreSQL.

## Why I built this

Everyone complains about load-shedding but nobody actually tracks it. I wanted real numbers instead of "the power's been terrible lately" - how often it happens, how long it usually lasts, whether it's getting worse. Also didn't want to build yet another basic to-do-list CRUD project, so this felt like a better use of the same skills.

## What it does and doesn't do

I kept the scope pretty tight on purpose:

- No login/accounts, it's just for me
- No notifications
- Doesn't hook into any live electricity provider API (couldn't find one that's actually reliable)
- No mobile app, just a normal web page

The whole flow is: log an outage → mark it resolved → duration gets calculated → saved to the database → shows up on the dashboard → also shows up in a chart → and it's available as JSON too if I ever want to use the data somewhere else.

## Features

- **Log an outage** - defaults to right now, but you can also backdate it if you're logging something that already happened. Can't put in a future date, that gets rejected both by the form and on the server.
- **Resolve** - sets the end time, and the duration is always calculated from start/end, never typed in directly. Means it can't be wrong or inconsistent.
- **Delete** - for mistakes or duplicates.
- **Dashboard** - shows some quick stats up top (how many outages, total hours without power, average length), a chart of outage duration by day, whatever's currently ongoing, and a scrollable history of everything that's been resolved.
- **JSON API** at `/api` and `/api/<id>` if you want the raw data.

## A couple of decisions I made

- Duration is never stored as its own number, it's always calculated from start_time and end_time. If I'd stored it separately it could end up wrong if I made a typo somewhere.
- You can log an outage after it already happened (useful since I usually remember to log it later, not right when the power actually cuts), but you still can't fake a future outage.
- The chart is generated on the server with matplotlib and sent over as an image, rather than doing it in JavaScript. Simpler, and I didn't want to pull in a whole charting library for one graph.

## Running it

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # fill in your own PostgreSQL details
createdb load_shedding

python app.py
```

`.env` gets loaded automatically, no extra steps needed there. Runs at `http://localhost:5001`. Tables get created automatically the first time you run it - fine for this, but if it ever needed to handle real schema changes I'd switch to Flask-Migrate instead.

## Project layout

load-shedding-logger/
├── app.py # routes: dashboard, log, resolve, delete, api
├── config.py # env-driven config (DB URI, secret key)
├── models.py # Outage model — duration is a computed property
├── forms.py # Flask-WTF forms (CSRF-protected)
├── analytics.py # builds the outage-duration chart (pandas + matplotlib)
├── requirements.txt
├── .env.example
└── templates/
  ├── base.html
  └── dashboard.html

## API

`GET /api` gives you something like:

```json
[
  {
    "id": 3,
    "start_time": "2026-08-15T04:12:00+00:00",
    "end_time": "2026-08-15T06:40:00+00:00",
    "status": "resolved",
    "duration_seconds": 8880,
    "duration_human": "2h 28m",
    "note": null
  }
]
```

## Stuff that's not perfect

- No login, so anyone with the URL could log or delete entries. Fine for personal use, not fine for anything shared.
- The "Location" field on the dashboard is really just the note field with a different label, not its own proper column. Would need to fix that if I ever wanted to track separate areas properly.
- This is running with Flask's dev server and debug mode on, which is fine locally but you'd never actually deploy it like this.