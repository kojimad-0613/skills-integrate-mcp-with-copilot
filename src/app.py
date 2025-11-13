"""
High School Management System API (DB-backed)

This version uses SQLModel for persistence. It reads `DATABASE_URL` from the
environment. If not provided, it falls back to a local SQLite file for
development convenience.
"""

import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from sqlmodel import Session, select, create_engine

from .models import SQLModel, Activity, Participant


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent, "static")), name="static")

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data.db")
engine = create_engine(DATABASE_URL, echo=False)


@app.on_event("startup")
def on_startup():
    # create tables if they don't exist
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    with Session(engine) as session:
        activities = session.exec(select(Activity)).all()
        result = {}
        for act in activities:
            participants = [p.email for p in act.participants]
            result[act.name] = {
                "description": act.description,
                "schedule": act.schedule,
                "max_participants": act.max_participants,
                "participants": participants,
            }
        return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    with Session(engine) as session:
        statement = select(Activity).where(Activity.name == activity_name)
        activity = session.exec(statement).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Load participants count
        current = len(activity.participants)
        if any(p.email == email for p in activity.participants):
            raise HTTPException(status_code=400, detail="Student is already signed up")

        if activity.max_participants and current >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        participant = Participant(email=email, activity_id=activity.id)
        session.add(participant)
        session.commit()
        session.refresh(participant)
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    with Session(engine) as session:
        statement = select(Activity).where(Activity.name == activity_name)
        activity = session.exec(statement).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant_stmt = select(Participant).where(Participant.activity_id == activity.id, Participant.email == email)
        participant = session.exec(participant_stmt).first()
        if not participant:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(participant)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}

