import random
from enum import Enum, auto

from constants import MONTHS_DATA, REF_WEEKDAY_YEARS


class GuessType(Enum):
    FULL_DATE = auto()       # Guess the weekday for a specific date
    YEAR_ONLY = auto()       # Guess the reference weekday for a specific year
    OFFSET_WEEKDAY = auto()  # Guess the weekday for a given offset and reference weekday
    MONTH_ONLY = auto()      # Guess all day offsets for a specific month
    DAY_MONTH_ONLY = auto()  # Guess the offset for a specific month and day
    ODD_11 = auto()          # Guess the offset for a given double-digit year ending


class Guess:
    # 7th of March has zero offset for any given year, and isn't affected by leap years
    DEFAULT_DAY: int = 7
    DEFAULT_MONTH: int = 3

    def __init__(self, guess_type: GuessType):
        self.type = guess_type
        self.day: int = 0  # also used as offset for OFFSET_WEEKDAY
        self.month: int = 0
        self.year: int = 0  # also used as ref_weekday for OFFSET_WEEKDAY

        match self.type:
            case GuessType.FULL_DATE:
                self.day, self.month = self._choose_day_month()
                self.year = self._choose_year()
            case GuessType.DAY_MONTH_ONLY:
                self.day, self.month = self._choose_day_month()
                # To make this work, the two years here have to have Monday as their
                # reference weekday, one being leap and the other one being non-leap
                self.year = 2016 if random.random() < 0.5 else 1994
            case GuessType.YEAR_ONLY:
                self.day = self.DEFAULT_DAY
                self.month = self.DEFAULT_MONTH
                self.year = self._choose_year()
            case GuessType.OFFSET_WEEKDAY:
                self.month = self.DEFAULT_MONTH
                self.day = random.randint(self.DEFAULT_DAY - 3, self.DEFAULT_DAY + 3)
                self.year = random.choice(list(REF_WEEKDAY_YEARS.values()))
            case GuessType.MONTH_ONLY:
                self.month = random.randint(1, 12)
            case GuessType.ODD_11:
                self.year = random.randint(0, 99)

    def __str__(self) -> str:
        from translate import TR  # circular import
        match self.type:
            case GuessType.YEAR_ONLY | GuessType.ODD_11:
                return str(self.year)
            case GuessType.MONTH_ONLY:
                return TR("months", self.month)
            case GuessType.FULL_DATE:
                return f"{self.day} {TR("months", self.month)} {self.year}"
            case GuessType.OFFSET_WEEKDAY:
                offset: int = self.day - self.DEFAULT_DAY
                ref_weekday: int = (self.answer() - offset) % 7
                return f"{offset:+d}  {TR("weekdays", ref_weekday)}"
            case GuessType.DAY_MONTH_ONLY:
                leap_text: str = ""
                if self.year == 0 and (self.month <= 2 or random.random() < 0.4):
                    leap_text = f" ({TR('leap')})"
                return f"{self.day} {TR("months", self.month)}{leap_text}"
        raise RuntimeError(f"Unsupported guess type: {self.type}")

    def _repr_tuple(self) -> tuple[GuessType, int, int, int]:
        return (self.type, self.day, self.month, self.year)

    def __hash__(self) -> int:
        return hash(self._repr_tuple())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Guess):
            return NotImplemented
        return self._repr_tuple() == other._repr_tuple()

    @property
    def leap(self) -> bool:
        return (self.year % 4 == 0 and self.year % 100 != 0) or (self.year % 400 == 0)

    def answer(self) -> int:
        # Returns the expected answer for the guess,
        # usually a number representing a weekday or offset
        # For GuessType.MONTH_ONLY, the answer is the day offset for a given month
        # NOTE: Only supports years 1901-2099
        month_offset: int = MONTHS_DATA[self.month][1]
        match self.type:
            case GuessType.MONTH_ONLY:
                return int(
                    ''.join(
                        str(i * 7 + month_offset)
                        for i in range(5)
                        if (i * 7 + month_offset) <= MONTHS_DATA[self.month][0]
                    )
                )
            case GuessType.ODD_11:
                a = self.year
                if a % 2 == 1:
                    a += 11
                a //= 2
                if a % 2 == 1:
                    a += 11
                return 7 - (a % 7)
            case (
                GuessType.FULL_DATE |
                GuessType.DAY_MONTH_ONLY |
                GuessType.YEAR_ONLY |
                GuessType.OFFSET_WEEKDAY
            ):
                a = (self.year + (self.year // 4) - month_offset + self.day) % 7
                if self.leap and self.month <= 2 and self.month > 0:
                    return (a - 1) % 7
                return a
        raise RuntimeError(f"Unsupported guess type: {self.type}")

    def answer_text(self) -> str:
        # Returns the expected answer as a string, formatted for display
        ans = self.answer()
        match self.type:
            case GuessType.DAY_MONTH_ONLY:
                return str(ans if ans < 4 else ans - 7)
            case GuessType.FULL_DATE | GuessType.YEAR_ONLY | GuessType.OFFSET_WEEKDAY:
                from translate import TR  # circular import
                return TR("weekdays", ans)
        return str(ans)

    def speak_guess(self) -> None:
        from translate import TR  # circular import
        TR.speak(str(self))

    def _choose_year(self) -> int:
        from settings import YEAR_MIN, YEAR_MAX  # circular import
        return random.randint(YEAR_MIN, YEAR_MAX)
        # return round(self.YEAR_MIN + random.betavariate(4, 4) * (self.YEAR_MAX - self.YEAR_MIN))

    def _choose_day_month(self) -> tuple[int, int]:
        month = random.randint(1, 12)
        mdays = MONTHS_DATA[month][0]
        if month == 2 and self.leap:
            mdays += 1
        day = random.randint(1, mdays)
        # return (30, 7)
        return (day, month)
