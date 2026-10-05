from datetime import date, datetime, time, timedelta

from bot.slots import ReminderState, Schedule, bookable_days, due_reminders, free_slots

SCH = Schedule(work_days=(0, 1, 2, 3, 4, 5), open_at=time(10), close_at=time(19),
               step=timedelta(minutes=30), min_lead=timedelta(hours=1), days_ahead=7)
MON = date(2026, 10, 5)            # a Monday
EARLY = datetime(2026, 10, 1, 9)   # long before, so min_lead does not interfere
H = timedelta(hours=1)


def test_full_free_day():
    slots = free_slots(MON, H, [], SCH, EARLY)
    assert slots[0] == datetime(2026, 10, 5, 10, 0)
    assert slots[-1] == datetime(2026, 10, 5, 18, 0)   # 18:00 + 1h ends exactly at close
    assert len(slots) == 17


def test_long_service_must_fit_before_close():
    slots = free_slots(MON, timedelta(minutes=90), [], SCH, EARLY)
    assert slots[-1] == datetime(2026, 10, 5, 17, 30)


def test_day_off():
    assert free_slots(date(2026, 10, 11), H, [], SCH, EARLY) == []   # Sunday


def test_busy_slot_blocks_overlaps_only():
    busy = [(datetime(2026, 10, 5, 12, 0), H)]
    slots = free_slots(MON, H, busy, SCH, EARLY)
    assert datetime(2026, 10, 5, 11, 30) not in slots   # would end 12:30, overlaps
    assert datetime(2026, 10, 5, 12, 30) not in slots
    assert datetime(2026, 10, 5, 11, 0) in slots        # ends at 12:00, touching is fine
    assert datetime(2026, 10, 5, 13, 0) in slots


def test_min_lead_hides_too_soon_slots():
    now = datetime(2026, 10, 5, 13, 10)
    slots = free_slots(MON, H, [], SCH, now)
    assert slots[0] == datetime(2026, 10, 5, 14, 30)


def test_bookable_days_skips_full_and_past_days():
    now = datetime(2026, 10, 5, 18, 30)   # Monday evening: no time left today
    days = bookable_days(H, [], SCH, now)
    assert MON not in days
    assert date(2026, 10, 6) in days
    assert date(2026, 10, 11) not in days   # Sunday


def state(start, created, s24=False, s2=False):
    return ReminderState(start=start, created=created, sent_24h=s24, sent_2h=s2)


START = datetime(2026, 10, 10, 15, 0)


def test_24h_reminder():
    r = state(START, datetime(2026, 10, 5, 12))
    assert due_reminders(r, datetime(2026, 10, 9, 14)) == []
    assert due_reminders(r, datetime(2026, 10, 9, 15)) == ["24h"]


def test_2h_reminder_after_24h_sent():
    r = state(START, datetime(2026, 10, 5, 12), s24=True)
    assert due_reminders(r, datetime(2026, 10, 10, 13)) == ["2h"]


def test_late_booking_skips_24h():
    r = state(START, datetime(2026, 10, 10, 9))
    assert due_reminders(r, datetime(2026, 10, 10, 13)) == ["2h"]


def test_offline_bot_sends_only_closest():
    r = state(START, datetime(2026, 10, 5, 12))
    assert due_reminders(r, datetime(2026, 10, 10, 14)) == ["2h"]


def test_no_stale_24h_after_2h_was_sent():
    r = state(START, datetime(2026, 10, 5, 12), s24=False, s2=True)
    assert due_reminders(r, datetime(2026, 10, 10, 14, 1)) == []


def test_no_reminders_after_start():
    r = state(START, datetime(2026, 10, 5, 12))
    assert due_reminders(r, datetime(2026, 10, 10, 15, 1)) == []
