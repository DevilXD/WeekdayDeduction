from __future__ import annotations

import random
from time import time, sleep
from collections import defaultdict

from translate import TR
from guess import Guess, GuessType
from constants import MAX_ANSWER_TIME
from settings import SLOW_MULTI, FAST_THRESHOLD, LOSE_INSTANTLY, USE_SPEECH
from utils import (  # noqa
    uinput,
    uinput2,
    wday_check,
    shift_check,
    value_check,
    get_guess_type,
    random_from_dict,
    get_repeat_chance,
    check_win_threshold,
)


# TR.set_language("English")  # use this to change language to any supported by the lang folder


fast: int = 0
good: int = 0
wrong: int = 0
good_sum: float = 0.0
fast_sum: float = 0.0


print()
repeat_flag: bool = False
last_guess: Guess | None = None
repeat_dates: defaultdict[Guess, int] = defaultdict(int)
while True:
    repeat_sum: int = sum(repeat_dates.values())
    score: float = fast + good * SLOW_MULTI
    win_threshold: float = check_win_threshold(100, wrong)
    progress: float = min(max(score / win_threshold, 0.0), 1.0)
    if score >= win_threshold and (repeat_sum <= 0 or score >= win_threshold * 2):
        print(
            TR("youve_won").format(
                score=f"{score:.1f}/{win_threshold}",
                good=good,
                good_avg=good_sum/good,
                fast=fast,
                slow=good-fast,
                fast_avg=fast_sum/fast,
                wrong=wrong
            )
        )
        break
    for _ in range(100):
        if repeat_flag and random.random() < get_repeat_chance(repeat_sum, progress):
            guess = random_from_dict(repeat_dates, k=1)
        else:
            guess = Guess(get_guess_type())
        if guess != last_guess:
            last_guess = guess
            break

    ask_time: float = time()
    exp_answer: int = guess.answer()
    if USE_SPEECH:
        guess.speak_guess()
    else:
        print(guess)
    print()
    score_text: str = f"{score:.1f}/{win_threshold:.1f}"
    match guess.type:
        case GuessType.MONTH_ONLY:
            usr_answer: int = uinput(
                TR("input", "ref_sequence").format(score=score_text),
                value_check,
            )
        case GuessType.DAY_MONTH_REF:
            usr_answer = uinput(
                TR("input", "closest_ref").format(score=score_text),
                value_check,
            )
        case GuessType.DAY_MONTH_ONLY:
            usr_answer = uinput(TR("input", "shift").format(score=score_text), shift_check)
        case _:
            # usr_answer = uinput(TR("input", "weekday").format(score=score_text), wday_check)
            usr_answer = uinput2(TR("input", "weekday").format(score=score_text))
    # Limit the max answer time
    answer_time: float = min(time() - ask_time, MAX_ANSWER_TIME)

    if usr_answer == exp_answer:
        good += 1
        good_sum += answer_time
        if answer_time < FAST_THRESHOLD:
            fast += 1
            fast_sum += answer_time
            repeat_flag = True
        elif repeat_sum > 30:
            repeat_flag = True
        if (attempts := repeat_dates.get(guess)) is not None:
            repeat_dates[guess] -= 1
            if repeat_dates[guess] <= 0:
                del repeat_dates[guess]
        elif answer_time >= FAST_THRESHOLD and score < win_threshold:
            repeat_dates[guess] += 1
        print(
            TR("good").format(
                repeat=sum(repeat_dates.values()),
                sign='>' if answer_time >= MAX_ANSWER_TIME else '',
                time=answer_time,
            )
        )
    else:
        wrong += 1
        repeat_flag = False
        repeat_dates[guess] += 5 if score < win_threshold else 1
        if LOSE_INSTANTLY:
            print(TR("lose").format(answer=guess.answer_text()))
            sleep(5)
            last_guess = None
            repeat_flag = False
            good = fast = wrong = 0
            good_sum = fast_sum = 0.0
            repeat_dates.clear()
        else:
            print(
                TR("wrong").format(
                    repeat=sum(repeat_dates.values()),
                    sign='>' if answer_time >= MAX_ANSWER_TIME else '',
                    time=answer_time,
                )
            )

    print()

# Highscore for DAY_MONTH_ONLY:
# You've won! Score: 100.5/100.0 (67 good (2.517s avg), 67/0 fast/slow (2.517s fast avg), 0 wrong)
