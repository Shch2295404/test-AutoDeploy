from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Time Server API", version="1.0.0")


def _parse_utc_instant(utc_iso: str | None) -> datetime:
    if utc_iso is None:
        return datetime.now(timezone.utc)
    text = utc_iso.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _format_utc_offset(dt: datetime) -> str:
    off = dt.utcoffset()
    if off is None:
        return "+00:00"
    secs = int(off.total_seconds())
    sign = "+" if secs >= 0 else "-"
    secs = abs(secs)
    h, r = divmod(secs, 3600)
    m = r // 60
    return f"{sign}{h:02d}:{m:02d}"


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


@app.get("/convert")
def utc_to_timezone(
    tz: str = Query(
        ...,
        description='IANA timezone, e.g. "Europe/Moscow", "Asia/Yekaterinburg"',
        examples=["Europe/Moscow", "America/New_York", "UTC"],
    ),
    utc_iso: str | None = Query(
        None,
        description="Instant in UTC as ISO 8601 (optional). If omitted, current server time (UTC) is used.",
    ),
):
    try:
        zone = ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown IANA timezone: {tz!r}. Examples: Europe/Moscow, Asia/Yekaterinburg.",
        ) from None
    utc_dt = _parse_utc_instant(utc_iso)
    local_dt = utc_dt.astimezone(zone)
    return {
        "timezone": tz,
        "utc_iso": utc_dt.isoformat(),
        "local_iso": local_dt.isoformat(),
        "utc_offset": _format_utc_offset(local_dt),
    }
