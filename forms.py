from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import Length, Optional, ValidationError

def not_in_future(form, field):
    if field.data and field.data.replace(tzinfo=None) > datetime.now():
        raise ValidationError("Can't log a date in the future.")
    
class LogOutageForm(FlaskForm):
    """Log a new outage - defaults to 'now' but can be backdated for
    outages that already happened (e.g. logging yesterday's cut today)."""

    note = StringField("Note (optional)", validators=[Optional(), Length(max=255)])
    start_time = DateTimeField(
        "Started Date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional(), not_in_future],
        render_kw={"type": "datetime-local"},
    )
    end_time = DateTimeField(
        "Ended Date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional(), not_in_future],
        render_kw={"type": "datetime-local"},
    )
    submit = SubmitField("Log outage")

class ResolveForm(FlaskForm):
    """Empty form, exists only to carry CSRF protection for the resolve button."""

    submit = SubmitField("Mark resolved")


class DeleteForm(FlaskForm):
    """Empty form, exists only to carry CSRF protection for the delete button."""

    submit = SubmitField("Delete")
