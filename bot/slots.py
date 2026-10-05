"""Calendar math: which days and times are free, and which reminders are due.

Pure functions with no Telegram or database code, so they are easy to test.
All datetimes are naive and in the business time zone.
"""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass(frozen=True)
class Schedule:
    work_days: tuple[int, ...]   # 0 = Monday
    open_at: time
    close_at: time
    step: timedelta              # how often a slot can start
    min_lead: timedelta          # earliest booking from "now"
    days_ahead: int


def overlaps(start: datetime, dur: timedelta, busy: list[tuple[datetime, timedelta]]) -> bool:
    end = start + dur
    return any(start < b_start + b_dur and b_start < end for b_start, b_dur in busy)


def free_slots(day: date, duration: timedelta, busy: list[tuple[datetime, timedelta]],
               sch: Schedule, now: datetime) -> list[datetime]:
    """Start times on `day` where a service of `duration` fits and nothing overlaps."""
    if day.weekday() not in sch.work_days:
        return []
    slot = datetime.combine(day, sch.open_at)
    close = datetime.combine(day, sch.close_at)
    earliest = now + sch.min_lead
    result = []
    while slot + duration <= close:
        if slot >= earliest and not overlaps(slot, duration, busy):
            result.append(slot)
        slot += sch.step
    return result


def day_grid(day: date, duration: timedelta, busy: list[tuple[datetime, timedelta]],
             sch: Schedule, now: datetime) -> list[tuple[datetime, bool]]:
    """Every start time of the working day with a flag "free".

    The keyboard shows the whole day and greys out taken or past times,
    so the client sees a real schedule rather than a few random buttons.
    """
    if day.weekday() not in sch.work_days:
        return []
    free = set(free_slots(day, duration, busy, sch, now))
    slot = datetime.combine(day, sch.open_at)
    close = datetime.combine(day, sch.close_at)
    grid = []
    while slot + duration <= close:
        grid.append((slot, slot in free))
        slot += sch.step
    return grid


def week_grid(duration: timedelta, busy: list[tuple[datetime, timedelta]],
              sch: Schedule, now: datetime) -> list[tuple[date, str]]:
    """Every day of the booking window with a status: "free", "off" (day off) or "full".

    Days off and fully booked days stay in the list, so the week reads like a calendar.
    """
    days = (now.date() + timedelta(days=i) for i in range(sch.days_ahead + 1))
    result = []
    for d in days:
        if d.weekday() not in sch.work_days:
            result.append((d, "off"))
        else:
            result.append((d, "free" if free_slots(d, duration, busy, sch, now) else "full"))
    return result


def bookable_days(duration: timedelta, busy: list[tuple[datetime, timedelta]],
                  sch: Schedule, now: datetime) -> list[date]:
    """Days in the booking window that still have at least one free slot."""
    days = (now.date() + timedelta(days=i) for i in range(sch.days_ahead + 1))
    return [d for d in days if free_slots(d, duration, busy, sch, now)]


@dataclass
class ReminderState:
    start: datetime
    created: datetime
    sent_24h: bool
    sent_2h: bool


def due_reminders(r: ReminderState, now: datetime) -> list[str]:
    """Which reminders to send now: "24h", "2h" or none.

    A reminder is skipped when the booking was made later than its moment:
    someone who books at 15:00 for 16:00 does not need a "tomorrow" message.
    """
    due = []
    for kind, before, sent in (("24h", timedelta(hours=24), r.sent_24h),
                               ("2h", timedelta(hours=2), r.sent_2h)):
        moment = r.start - before
        if not sent and moment <= now < r.start and r.created < moment:
            due.append(kind)
    if r.sent_2h and "24h" in due:
        due.remove("24h")   # the 2h one already went out, a "tomorrow" message would be wrong
    # If the bot was offline and both became due, only the closer one matters.
    return ["2h"] if "2h" in due else due
