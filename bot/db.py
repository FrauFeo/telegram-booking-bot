"""SQLite storage for users and bookings.

Plain sqlite3: every query here takes well under a millisecond, so the extra
complexity of an async driver is not worth it for a bot of this size.
"""
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang    TEXT NOT NULL DEFAULT 'uk'
);
CREATE TABLE IF NOT EXISTS bookings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    name       TEXT NOT NULL,
    phone      TEXT NOT NULL,
    service_id TEXT NOT NULL,
    start      TEXT NOT NULL,          -- local time, ISO format
    duration   INTEGER NOT NULL,       -- minutes
    status     TEXT NOT NULL DEFAULT 'pending',   -- pending / confirmed / cancelled
    created    TEXT NOT NULL,
    sent_24h   INTEGER NOT NULL DEFAULT 0,
    sent_2h    INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS bookings_start ON bookings(start);
"""


@dataclass
class Booking:
    id: int
    user_id: int
    name: str
    phone: str
    service_id: str
    start: datetime
    duration: timedelta
    status: str
    created: datetime
    sent_24h: bool
    sent_2h: bool

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Booking":
        return cls(
            id=row["id"], user_id=row["user_id"], name=row["name"], phone=row["phone"],
            service_id=row["service_id"], start=datetime.fromisoformat(row["start"]),
            duration=timedelta(minutes=row["duration"]), status=row["status"],
            created=datetime.fromisoformat(row["created"]),
            sent_24h=bool(row["sent_24h"]), sent_2h=bool(row["sent_2h"]),
        )


class DB:
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    # users
    def get_lang(self, user_id: int) -> str | None:
        row = self.conn.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row["lang"] if row else None

    def set_lang(self, user_id: int, lang: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO users(user_id, lang) VALUES(?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang", (user_id, lang))

    # bookings
    def busy(self, start_from: datetime, until: datetime) -> list[tuple[datetime, timedelta]]:
        """Occupied intervals between two moments, cancelled bookings excluded."""
        rows = self.conn.execute(
            "SELECT start, duration FROM bookings "
            "WHERE status != 'cancelled' AND start >= ? AND start < ?",
            (start_from.isoformat(), until.isoformat())).fetchall()
        return [(datetime.fromisoformat(r["start"]), timedelta(minutes=r["duration"])) for r in rows]

    def add(self, user_id: int, name: str, phone: str, service_id: str,
            start: datetime, duration: timedelta, now: datetime) -> int:
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO bookings(user_id, name, phone, service_id, start, duration, created) "
                "VALUES(?, ?, ?, ?, ?, ?, ?)",
                (user_id, name, phone, service_id, start.isoformat(),
                 int(duration.total_seconds() // 60), now.isoformat()))
        return cur.lastrowid

    def get(self, booking_id: int) -> Booking | None:
        row = self.conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        return Booking.from_row(row) if row else None

    def set_status(self, booking_id: int, status: str) -> None:
        with self.conn:
            self.conn.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))

    def upcoming_for_user(self, user_id: int, now: datetime) -> list[Booking]:
        rows = self.conn.execute(
            "SELECT * FROM bookings WHERE user_id = ? AND status != 'cancelled' AND start >= ? "
            "ORDER BY start", (user_id, now.isoformat())).fetchall()
        return [Booking.from_row(r) for r in rows]

    def between(self, start_from: datetime, until: datetime) -> list[Booking]:
        rows = self.conn.execute(
            "SELECT * FROM bookings WHERE status != 'cancelled' AND start >= ? AND start < ? "
            "ORDER BY start", (start_from.isoformat(), until.isoformat())).fetchall()
        return [Booking.from_row(r) for r in rows]

    def mark_reminded(self, booking_id: int, kind: str) -> None:
        column = {"24h": "sent_24h", "2h": "sent_2h"}[kind]
        with self.conn:
            self.conn.execute(f"UPDATE bookings SET {column} = 1 WHERE id = ?", (booking_id,))
