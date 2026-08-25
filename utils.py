from __future__ import annotations

import json
import math
import msvcrt
import random
import unicodedata
from pathlib import Path
from copy import deepcopy
from collections import abc

from typing import Any, TypeAlias, TypeVar, overload, cast, TYPE_CHECKING

from settings import GUESS_CHANCES

if TYPE_CHECKING:
    from guess import GuessType


T = TypeVar('T')
JsonType: TypeAlias = "dict[str, Any]"
_JSON_T = TypeVar("_JSON_T", bound=abc.Mapping[str, Any])


def uinput(prompt: str, convert: abc.Callable[[str], tuple[str, int] | None]) -> int:
    """
    Process user input in a similar way input() does it.

    Upon pressing Enter, convert the input text via the convert() function call,
    which returns tuple[str, int].
    The 'str' is shown to the user, the 'int' is the return value.

    This is primarily used to show the full name of the weekday, while returning it's offset.
    """
    while True:
        print('\r', end='')
        print(prompt, end='')
        keys: list[str] = []
        while True:
            key: str = msvcrt.getwch()
            if key == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif key == '\b':  # Backspace
                if keys:
                    keys.pop()
                    print('\b \b', end='')
                continue
            elif key == '\r':  # Enter
                break
            keys.append(key)
            print(key, end='')
        keys_joined: str = ''.join(keys)
        # clear the input line, reposition cursor
        print(
            '\b' * (len(keys_joined) + 1),
            ' ' * len(keys_joined),
            '\b' * (len(keys_joined) + 1),
            end=''
        )
        result: tuple[str, int] | None = convert(keys_joined)
        if result is None:
            continue  # Ask again
        print(result[0])
        return result[1]


def uinput2(prompt: str) -> int:
    """
    Process user input by listening to single key presses. No pressing Enter is required.

    Charmap:
    • Z: Monday
    • X: Tuesday
    • C: Wednesday
    • V: Thursday
    • B: Friday
    • N: Saturday
    • M: Sunday
    """
    while True:
        print('\r', end='')
        print(prompt, end='')
        wday: int | None = None
        while True:
            key: str = msvcrt.getwch()
            if key == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
            elif key == 'z':
                wday = 0
            elif key == 'x':
                wday = 1
            elif key == 'c':
                wday = 2
            elif key == 'v':
                wday = 3
            elif key == 'b':
                wday = 4
            elif key == 'n':
                wday = 5
            elif key == 'm':
                wday = 6
            if wday is not None:
                from translate import TR  # circular import
                print(TR("weekdays", wday))
                return wday


def parse_weekday(text: str) -> int | None:
    """
    Parse incomplete text into an unambiguous weekday offset.
    """
    text = text.strip().lower()
    from translate import TR  # circular import
    all_weekdays: dict[int, str] = cast("dict[int, str]", TR("weekdays"))

    # Numeric input support
    if text.isdigit():
        number = int(text)
        return number if number in all_weekdays else None

    # Text matching
    text = normalize_unicode(text)
    matches: set[int] = set()
    for number, name in all_weekdays.items():
        if normalize_unicode(name).startswith(text):
            matches.add(number)
    if len(matches) == 1:
        return matches.pop()
    return None


def wday_check(text: str) -> tuple[str, int] | None:
    """
    Convert incomplete text into a (weekday, offset) pair.
    Returns None when the conversion fails.
    """
    wday: int | None = parse_weekday(text)
    if wday is None:
        return None
    from translate import TR  # circular import
    return (TR("weekdays", wday), wday)


def value_check(text: str) -> tuple[str, int] | None:
    """
    Simple int parser.
    Returns None when the conversion fails.
    """
    text = text.strip().lower()
    try:
        value = int(text)
    except ValueError:
        return None
    return str(value), value


def offset_check(text: str) -> tuple[str, int] | None:
    """
    Int parser, but limits the valid value range to <-6, 6>.
    Returns None when the conversion fails, or the value is out of range.
    """
    result = value_check(text)
    if result is None:
        return None
    _, offset = result
    if -6 < offset > 6:
        return None
    return str(offset), offset % 7


def normalize_unicode(text: str) -> str:
    """
    Remove accents; allows you to use just the base letters of a word.
    """
    text = text.strip().lower()
    return ''.join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


@overload
def random_from_dict(d: abc.Mapping[T, float], k: int = 1, reverse: bool = False) -> T:
    ...


@overload
def random_from_dict(d: abc.Mapping[T, float], k: int, reverse: bool = False) -> list[T]:
    ...


def random_from_dict(d: abc.Mapping[T, float], k: int = 1, reverse: bool = False) -> T | list[T]:
    assert k > 0
    if reverse:
        sum_weights = sum(d.values())
        weights = [sum_weights - w for w in d.values()]
    else:
        weights = list(d.values())
    items: list[T] = random.choices(
        population=list(d.keys()),
        weights=weights,
        k=1
    )
    if k > 1:
        return items
    return items[0]


def get_guess_type() -> GuessType:
    return random_from_dict(GUESS_CHANCES, k=1)


def check_win_threshold(
    base: int,        # base threshold to pass
    wrong: int,       # amount of wrong guesses
    le: int = 2,      # lower error threshold before difficulty starts increasing
    ue: int = 10,     # upper error threshold specifying maximum difficulty
    md: float = 2.0,  # maximum difficulty multiplier
) -> float:
    assert le < ue
    assert ue - le > 0
    return base * min(1 + (1 / (ue - le)) * max(wrong - 2, 0), md)


def get_repeat_chance(
    repeat_sum: int,        # amount of repeats remaining
    progress: float,        # 0-1 progress of the round
    x_limit: int = 20,      # the chance for this limit maxes at y_limit percent
    y_one: float = 0.3,     # the pinned chance for the "1 / x_limit" case
    y_limit: float = 0.8,   # max chance
) -> float:
    assert x_limit > 0
    assert repeat_sum >= 0
    assert y_one + 0.01 < y_limit <= 1.0
    assert 0.0 <= progress <= 1.0
    if progress >= 1.0:
        # for a finished game, the repeat chance is max if there are repeat cases left,
        # otherwise its zero
        return 0.0 if repeat_sum <= 0 else y_limit
    exponent: float = math.log((y_one / y_limit) * (1 - progress)) / math.log(1 / x_limit)
    curve: float = min(repeat_sum / x_limit, 1) ** exponent
    return min(y_limit, y_limit * (curve / (1 - progress)))


# This below is to support saving/loading integer keys in dictionaries via JSON
def _int_key_save(obj: Any) -> Any:
    if isinstance(obj, abc.Mapping):
        result: dict[Any, JsonType] = {}
        for key, value in obj.items():
            if isinstance(key, int):
                result[str(key)] = {
                    "_int_key": True,
                    "value": _int_key_save(value),
                }
            else:
                result[key] = _int_key_save(value)
        return result
    elif isinstance(obj, list):
        return [_int_key_save(item) for item in obj]
    return obj


def _int_key_load(obj: Any) -> Any:
    if isinstance(obj, dict):
        result: dict[Any, JsonType] = {}
        for key, value in obj.items():
            restored_value = _int_key_load(value)
            # Was this originally an integer key?
            if (
                isinstance(restored_value, dict)
                and restored_value.get("_int_key") is True
                and "value" in restored_value
                and len(restored_value) == 2
            ):
                try:
                    int_key: int = int(key)
                except (TypeError, ValueError):
                    result[key] = restored_value
                else:
                    result[int_key] = restored_value["value"]
            else:
                result[key] = restored_value
        return result
    if isinstance(obj, list):
        return [_int_key_load(item) for item in obj]
    return obj


def merge_json(obj: JsonType, template: abc.Mapping[Any, Any]) -> None:
    # NOTE: This modifies object in place
    for k, v in list(obj.items()):
        if k not in template:
            # unknown key: overwrite from template
            del obj[k]
        elif type(v) is not type(template[k]):
            # types don't match: overwrite from template
            obj[k] = template[k]
        elif isinstance(v, dict):
            assert isinstance(template[k], dict)
            merge_json(v, template[k])
    # ensure the object is not missing any keys
    for k in template.keys():
        if k not in obj:
            obj[k] = template[k]


def json_load(path: Path, defaults: _JSON_T, *, merge: bool = True) -> _JSON_T:
    new_path: Path = path.with_name(f"{path.name}.new")
    combined: JsonType | None = None
    # try new file first
    if new_path.exists():
        try:
            with new_path.open('r', encoding="utf8") as file:
                combined = _int_key_load(json.load(file))
        except json.JSONDecodeError:
            # remove invalid file
            new_path.unlink()
    # try the old file
    if combined is None and path.exists():
        with path.open('r', encoding="utf8") as file:
            combined = _int_key_load(json.load(file))
    # handle defaults and merging
    if combined is None:
        combined = dict(defaults)  # always make a copy of defaults
    elif merge:
        merge_json(combined, dict(defaults))
    return cast(_JSON_T, combined)


def json_save(path: Path, contents: abc.Mapping[Any, Any], *, sort: bool = False) -> None:
    new_path: Path = path.with_name(f"{path.name}.new")
    new_contents = _int_key_save(deepcopy(contents))
    with new_path.open('w', encoding="utf8") as file:
        json.dump(new_contents, file, sort_keys=sort, indent=4)
    new_path.replace(path)
