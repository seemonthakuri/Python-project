from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Optional


class LogOutageForm(FlaskForm):
    """Start logging a new outage - start_time is set server-side to 'now'."""

    note = StringField("Note (optional)", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Log outage now")


class ResolveForm(FlaskForm):
    """Empty form, exists only to carry CSRF protection for the resolve button."""

    submit = SubmitField("Mark resolved")


class DeleteForm(FlaskForm):
    """Empty form, exists only to carry CSRF protection for the delete button."""

    submit = SubmitField("Delete")
