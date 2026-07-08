import random
from enum import Enum, auto

from constants import MONTHS_DATA


class GuessType(Enum):
    FULL_DATE = auto()       # Guess the weekday for a specific date
    YEAR_ONLY = auto()       # Guess the reference weekday for a specific year
    MONTH_ONLY = auto()      # Guess the day offsets for a specific month
    DAY_MONTH_ONLY = auto()  # Guess the total offset for a specific month and day
    DAY_MONTH_REF = auto()   # Guess the closest reference day for a given month and day


class Guess:
    def __init__(self, guess_type: GuessType):
        self.type = guess_type
        self.day: int = 0
        self.month: int = 0
        self.year: int = 0

        if self.type in (GuessType.YEAR_ONLY, GuessType.FULL_DATE):
            self.year = self._choose_year()
        elif self.type == GuessType.DAY_MONTH_ONLY:
            self.year = 0 if random.random() < 0.5 else 1
        elif self.type == GuessType.DAY_MONTH_REF:
            self.year = 1  # Prevents the "(leap)" text from appearing

        if self.type == GuessType.MONTH_ONLY:
            self.month = random.randint(1, 12)

        if self.type in (GuessType.DAY_MONTH_ONLY, GuessType.DAY_MONTH_REF, GuessType.FULL_DATE):
            self.day, self.month = self._choose_day_month()

    def __str__(self) -> str:
        from translate import TR  # circular import
        match self.type:
            case GuessType.DAY_MONTH_ONLY | GuessType.DAY_MONTH_REF:
                leap_text: str = ""
                if self.year == 0 and (self.month <= 2 or random.random() < 0.4):
                    leap_text = f" ({TR('leap')})"
                return f"{self.day} {TR("months", self.month)}{leap_text}"
            case GuessType.YEAR_ONLY:
                return str(self.year)
            case GuessType.MONTH_ONLY:
                return TR("months", self.month)
            case GuessType.FULL_DATE:
                return f"{self.day} {TR("months", self.month)} {self.year}"
        return ''  # failsafe

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
        if self.type is not GuessType.YEAR_ONLY:
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
            case GuessType.DAY_MONTH_REF:
                mod_offset = month_offset % 7
                if self.leap and self.month <= 2:
                    mod_offset = (mod_offset + 1) % 7
                test_days = [7 * i + mod_offset for i in range(5)]
                for i, d in enumerate(test_days):
                    if d == self.day:
                        return self.day
                    elif d > self.day:
                        if i == 0:
                            return d
                        elif d > MONTHS_DATA[self.month][0]:
                            return test_days[i-1]
                        return d if d - self.day < self.day - test_days[i-1] else test_days[i-1]
                return test_days[-1]
            case GuessType.DAY_MONTH_ONLY:
                a = (self.day - month_offset) % 7
            case GuessType.YEAR_ONLY:
                a = (self.year + (self.year // 4)) % 7
            case GuessType.FULL_DATE:
                a = (self.year + (self.year // 4) - month_offset + self.day) % 7
        if self.leap and self.month <= 2 and self.month > 0:
            a = (a - 1) % 7
        return a

    def answer_text(self) -> str:
        # Returns the expected answer as a string, formatted for display
        ans = self.answer()
        match self.type:
            case GuessType.DAY_MONTH_ONLY:
                return str(ans if ans < 4 else ans - 7)
            case GuessType.FULL_DATE | GuessType.YEAR_ONLY:
                from translate import TR  # circular import
                return TR("weekdays", ans)
            case _:
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
