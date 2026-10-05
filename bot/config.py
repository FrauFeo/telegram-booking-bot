"""Settings: secrets from .env, business details from config.json."""
import json
import os
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .slots import Schedule

ROOT = Path(__file__).resolve().parent.parent


def _load_env(path: Path) -> None:
    """Minimal .env reader, so the bot needs no extra package for it."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


@dataclass(frozen=True)
class Service:
    id: str
    names: dict[str, str]
    duration: timedelta
    price: int

    def name(self, lang: str) -> str:
        return self.names.get(lang) or next(iter(self.names.values()))


@dataclass(frozen=True)
class Settings:
    token: str
    admin_ids: frozenset[int]
    demo_mode: bool
    db_path: Path
    business: dict[str, str]
    currency: dict[str, str]
    tz: ZoneInfo
    schedule: Schedule
    services: dict[str, Service]

    def now(self) -> datetime:
        """Current time in the business time zone, naive like everything we store."""
        return datetime.now(self.tz).replace(tzinfo=None)


def load_settings() -> Settings:
    _load_env(ROOT / ".env")
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

    open_at, close_at = (time.fromisoformat(t) for t in cfg["work_hours"])
    schedule = Schedule(
        work_days=tuple(cfg["work_days"]),
        open_at=open_at,
        close_at=close_at,
        step=timedelta(minutes=cfg.get("slot_step_min", 30)),
        min_lead=timedelta(minutes=cfg.get("min_lead_min", 60)),
        days_ahead=cfg.get("days_ahead", 7),
    )
    services = {
        s["id"]: Service(s["id"], s["name"], timedelta(minutes=s["duration"]), s["price"])
        for s in cfg["services"]
    }
    admins = os.environ.get("ADMIN_IDS", "")
    return Settings(
        token=os.environ.get("BOT_TOKEN", ""),
        admin_ids=frozenset(int(x) for x in admins.split(",") if x.strip().isdigit()),
        demo_mode=os.environ.get("DEMO_MODE", "0") == "1",
        db_path=ROOT / os.environ.get("DB_PATH", "bookings.db"),
        business=cfg["business_name"],
        currency=cfg["currency"],
        tz=ZoneInfo(cfg.get("timezone", "Europe/Kyiv")),
        schedule=schedule,
        services=services,
    )
