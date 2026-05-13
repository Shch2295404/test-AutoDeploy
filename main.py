from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Time Server API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Добро пожаловать в Time Server API"}


@app.get("/time")
def server_time_utc():
    return {"time_utc": datetime.now(timezone.utc).isoformat()}


@app.get("/date")
def server_date_utc():
    now = datetime.now(timezone.utc)
    return {"date_utc": now.date().isoformat()}


@app.get("/datetime")
def server_datetime_utc():
    now = datetime.now(timezone.utc)
    return {"datetime_utc": now.isoformat()}
