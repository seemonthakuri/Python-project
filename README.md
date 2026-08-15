# Load-Shedding Logger

A simple Flask app to log power outages: start an entry when the power
goes out, mark it resolved when it comes back, and let the duration be
calculated automatically instead of typed in by hand. Backed by
PostgreSQL via SQLAlchemy.

## Features

- **Log outage** — one click, timestamps `start_time` server-side.
- **Resolve outage** — sets `end_time`; duration is derived, never stored raw.
- **Delete** — remove false/duplicate entries.
- **Dashboard** (`/`) — ongoing outages + resolved history, start/end/duration.
- **JSON API** (`/api`, `/api/<id>`) — all outages as JSON.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env with your PostgreSQL creds
createdb load_shedding          # or create the DB however you normally do

export $(grep -v '^#' .env | xargs)   # load .env into the shell (or use python-dotenv)
python app.py
```

The app runs at `http://localhost:5000`. Tables are created automatically
on first run via `db.create_all()` — for anything beyond local/dev use,
swap that for proper Flask-Migrate migrations.

## Project layout

```
load-shedding-logger/
├── app.py            # routes: dashboard, log, resolve, delete, api
├── config.py         # env-driven config (DB URI, secret key)
├── models.py         # Outage model — duration is a computed property
├── forms.py          # Flask-WTF forms (CSRF-protected)
├── requirements.txt
├── .env.example
└── templates/
    ├── base.html
    └── dashboard.html
```

## API

`GET /api` returns:

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

## Notes / next steps

- Duration is always computed from `start_time`/`end_time`, so it can't
  drift out of sync — that's the "no false entries" requirement from the
  concept note.
- Currently single-user/no auth. If this becomes a household tool, add a
  location/feeder field so different circuits can be tracked separately.
- For production, set a real `SECRET_KEY`, turn `debug` off, and put this
  behind gunicorn + a reverse proxy.
