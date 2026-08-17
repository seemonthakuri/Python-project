from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class Outage(db.Model):
    """A single power-outage record.

    Lifecycle:
      1. Created via POST /log  -> start_time set, end_time NULL (status='ongoing')
      2. Closed via POST /resolve/<id> -> end_time set (status='resolved')
      3. Duration is NEVER stored/typed by hand - it's always derived from
         start_time/end_time so it can't drift out of sync or be faked.
      4. Bad/duplicate entries are removed via POST /delete/<id>.
    """

    __tablename__ = "outages"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    @property
    def status(self):
        return "resolved" if self.end_time else "ongoing"

    @property
    def duration_seconds(self):
        """Automatically-derived duration in seconds. None while ongoing."""
        if not self.end_time:
            return None
        return (self.end_time - self.start_time).total_seconds()

    @property
    def duration_human(self):
        """Human-readable duration, e.g. '2h 15m'. Empty string if ongoing."""
        if not self.end_time:
            return ""
        rd = relativedelta(self.end_time, self.start_time)
        parts = []
        if rd.days:
            parts.append(f"{rd.days}d")
        if rd.hours:
            parts.append(f"{rd.hours}h")
        if rd.minutes:
            parts.append(f"{rd.minutes}m")
        if not parts:
            # outage lasted under a minute — don't render a blank duration
            return "<1m"
        return " ".join(parts)

    def resolve(self):
        """Mark this outage resolved right now. No-op if already resolved."""
        if not self.end_time:
            self.end_time = utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "duration_human": self.duration_human,
            "note": self.note,
        }
