from flask import Flask, render_template, redirect, url_for, flash, jsonify, abort

from datetime import datetime, timezone
from config import Config
from models import db, Outage, utcnow
from forms import LogOutageForm, ResolveForm, DeleteForm
from analytics import build_outage_chart


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def register_routes(app):
    @app.route("/", methods=["GET"])
    def dashboard():
        log_form = LogOutageForm()
        resolve_form = ResolveForm()
        delete_form = DeleteForm()

        outages = Outage.query.order_by(Outage.start_time.desc()).all()
        ongoing = [o for o in outages if o.status == "ongoing"]
        resolved = [o for o in outages if o.status == "resolved"]
        chart_data = build_outage_chart(outages)
        resolved_count = len(resolved)
        total_seconds = sum(o.duration_seconds for o in resolved)
        total_hours = round(total_seconds / 3600, 1) if resolved else 0

        if resolved_count:
            avg_seconds = total_seconds / resolved_count
            avg_hours, avg_minutes = divmod(int(avg_seconds // 60), 60)
        else:
            avg_hours, avg_minutes = 0, 0

        now = datetime.now()

        return render_template(
         "dashboard.html",
            ongoing=ongoing,
            resolved=resolved,
            log_form=log_form,
            resolve_form=resolve_form,
            delete_form=delete_form,
            chart_data=chart_data,
            resolved_count=resolved_count,
            total_hours=total_hours,
            avg_hours=avg_hours,
            avg_minutes=avg_minutes,
            now=now
        )
        
    @app.route("/log", methods=["POST"])
    def log_outage():
        form = LogOutageForm()
        if form.validate_on_submit():
            start = form.start_time.data or utcnow()
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)

            end = form.end_time.data
            if end is not None and end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)

            if end is not None and end <= start:
                flash("End time must be after the start time.", "error")
                return redirect(url_for("dashboard"))

            outage = Outage(note=form.note.data or None, start_time=start, end_time=end)
            db.session.add(outage)
            db.session.commit()
            flash("Outage logged.", "success")
        else:
            flash("Couldn't log outage - check the form.", "error")
        return redirect(url_for("dashboard"))

    @app.route("/resolve/<int:outage_id>", methods=["POST"])
    def resolve_outage(outage_id):
        form = ResolveForm()
        outage = Outage.query.get_or_404(outage_id)
        if form.validate_on_submit():
            outage.resolve()
            db.session.commit()
            flash(f"Outage #{outage.id} marked resolved ({outage.duration_human}).", "success")
        else:
            flash("Couldn't resolve outage.", "error")
        return redirect(url_for("dashboard"))

    @app.route("/delete/<int:outage_id>", methods=["POST"])
    def delete_outage(outage_id):
        form = DeleteForm()
        outage = Outage.query.get_or_404(outage_id)
        if form.validate_on_submit():
            db.session.delete(outage)
            db.session.commit()
            flash(f"Outage #{outage_id} removed.", "success")
        else:
            flash("Couldn't delete outage.", "error")
        return redirect(url_for("dashboard"))

    @app.route("/api", methods=["GET"])
    def api_outages():
        outages = Outage.query.order_by(Outage.start_time.desc()).all()
        return jsonify([o.to_dict() for o in outages])

    @app.route("/api/<int:outage_id>", methods=["GET"])
    def api_outage_detail(outage_id):
        outage = Outage.query.get(outage_id)
        if outage is None:
            abort(404)
        return jsonify(outage.to_dict())


app = create_app()

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)