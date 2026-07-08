from pathlib import Path

# SELF_PATH = Path(sys.argv[0]).resolve()
SELF_PATH = Path(__file__).resolve()
WORKING_DIR = SELF_PATH.parent
LANG_PATH = Path(WORKING_DIR, "lang")

MAX_ANSWER_TIME: float = 60.0

MONTHS_DATA: dict[int, tuple[int, int]] = {
    0:  (30, 0),  # placeholder for index 0
    1:  (31, 3),
    2:  (28, 0),
    3:  (31, 0),
    4:  (30, 4),
    5:  (31, 2),
    6:  (30, 6),
    7:  (31, 4),
    8:  (31, 1),
    9:  (30, 5),
    10: (31, 3),
    11: (30, 7),
    12: (31, 5),
}

REF_WEEKDAY_YEARS: dict[int, int] = {
    0: 2005,  # Monday
    1: 2006,  # Tuesday
    2: 2007,  # Wednesday
    3: 2002,  # Thursday
    4: 2003,  # Friday
    5: 2009,  # Saturday
    6: 2010,  # Sunday
}

_LOCAL_LANG_PATH = Path("local.lang")
LOCAL_LANG: str | None = None
if _LOCAL_LANG_PATH.exists():
    with _LOCAL_LANG_PATH.open('r', encoding="utf8") as file:
        LOCAL_LANG = file.read().strip()
