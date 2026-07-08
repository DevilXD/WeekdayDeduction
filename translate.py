from __future__ import annotations

from collections import abc

from typing import Any

from constants import LANG_PATH, LOCAL_LANG
from utils import JsonType, json_save, json_load

import yapper


default_translation: JsonType = {
    "weekdays": {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    },
    "months": {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    },
    "speaker": {
        # yapper-tts supported speaker names:
        # Belgium, Brazil, Catalonia, China, Congo, Czech, Denmark, Finland, France, GB, Georgia,
        # Germany, Greece, Hungary, Iceland, Iran, Italy, Jordan, Kazakhstan, Latvia, Luxembourg,
        # Mexico, Nepal, Netherlands, Norway, Poland, Portugal, Romania, Russia, Serbia, Slovakia,
        # Slovenia, Spain, Sweden, Turkey, Ukraine, US, Vietnam, Wales
        "name": "US",
        # Flavors are language-dependent - see yapper-tts documentation
        "flavor": "AMY",
    },
    "leap": "leap",
    "good": "Good! ({repeat} repeats) ({sign}{time:.2f} s)",
    "wrong": "Wrong! ({repeat} repeats) ({sign}{time:.2f} s)",
    "youve_won": (
        "You've won! Score: {score} ({good} good ({good_avg:.3f}s avg), {fast}/{slow} fast/slow "
        "({fast_avg:.3f}s fast avg), {wrong} wrong)"
    ),
    "lose": "You lose! The correct answer was: {answer}",
    "input": {
        "weekday": "Input weekday ({score}): ",
        "offset": "Input the offset value ({score}): ",
        "ref_sequence": "Input the reference days sequence ({score}): ",
    }
}


class Translator:
    DEFAULT_LANG: str = "English"

    def __init__(self) -> None:
        self._langs: list[str] = []
        # start with (and always copy) the default translation
        self._translation: JsonType = default_translation.copy()
        # update the template English.json file
        json_save(LANG_PATH.joinpath(f"{self.DEFAULT_LANG}.json"), default_translation)
        self._translation["language_name"] = self.DEFAULT_LANG
        # load available translation names
        for filepath in LANG_PATH.glob("*.json"):
            self._langs.append(filepath.stem)
        self._langs.sort()
        if self.DEFAULT_LANG in self._langs:
            self._langs.remove(self.DEFAULT_LANG)
        self._langs.insert(0, self.DEFAULT_LANG)
        # set local lang if possible
        if LOCAL_LANG is not None:
            self.set_language(LOCAL_LANG)

        # Speaker init
        speaker_key: dict[str, str] = self._translation["speaker"]
        speaker_flavor: yapper.enums.PiperVoice = getattr(
            getattr(yapper, f"PiperVoice{speaker_key['name']}"), speaker_key["flavor"]
        )
        self._speaker = yapper.PiperSpeaker(voice=speaker_flavor)

    @property
    def languages(self) -> abc.Iterable[str]:
        return iter(self._langs)

    @property
    def current(self) -> str:
        return self._translation["language_name"]

    def speak(self, text: str) -> None:
        self._speaker.say(text)

    def set_language(self, language: str):
        if language not in self._langs:
            raise ValueError("Unrecognized language")
        elif self._translation["language_name"] == language:
            # same language as loaded selected
            return
        elif language == self.DEFAULT_LANG:
            # default language selected - use the memory value
            self._translation = default_translation.copy()
        else:
            self._translation = json_load(
                LANG_PATH.joinpath(f"{language}.json"), default_translation
            )
            if "language_name" in self._translation:
                raise ValueError("Translations cannot define 'language_name'")
        self._translation["language_name"] = language

    def __call__(self, *path: str | int) -> str:
        if not path:
            raise ValueError("Language path expected")
        v: Any = self._translation
        try:
            for key in path:
                v = v[key]
        except KeyError:
            # this can only really happen for the default translation
            raise RuntimeError(
                f"{self.current} translation is missing the "
                f"'{' -> '.join(map(str, path))}' translation key"
            )
        return v


TR = Translator()
