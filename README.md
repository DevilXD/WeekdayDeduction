# WeekdayGuesser

A simple Python script that interrogates your weekday-deduction/guessing skills.

> [!Note]
> Requires Python 3.10+.

---

# Theory

It’s possible for you to deduce the weekday of any given date, by following a simple mental algorithm based on the [Doomsday rule](https://en.wikipedia.org/wiki/Doomsday_rule). The Doomsday Algorithm is a method developed by mathematician John Conway, who famously was able to deduce the weekday of any given date in under two seconds.

To compute the weekday of a particular date, you have to find a reference weekday for a given year first, and then apply an offset based on the combined month and day of the month.

> [!Note]
> For simplicity's sake, the explanation below is intentionally modified and limited to a **1900-2099** theoretical range, and **1980-2020** practical range. See the "Extending the years range" section at the end for more information.
>
> The intended purpose of this is to use it as a party trick for deducing the weekday on which another person was born on. This works for any other date from within the theoretical range though.

---

## Glossary

- Leap year - A year that is either divisible by 400, or is divisible by 4 and isn't divisible by 100. For the practical range, this can be reduced to a simple "divisible by 4" rule.
- Reference weekday/year/decade/century - The "doomsday weekday" associated with a given year, decade or century, usually represented as a precomputed pair of a year and its reference weekday in form of "YYYY-Weekday" for convenience.
- Anchor date - A fixed "day/month" pair, that defines the point in a year where the year’s reference weekday matches the weekday of that date. The first number is always the amount of days within a month, not the number representing the month itself.

All calculations related to weekdays have to be done by applying the **"modulo 7" (%)** operation on the result. This allows the weekdays to rotate around from Sunday back to Monday when going up, and Monday to Sunday when going down. For the purposes of this explanation, the following weekday representation offset values are used:

|   Weekday | +Offset | -Offset |
| :-------: | :-----: | :-----: |
|    Monday |  0 / +7 |  0 / -7 |
|   Tuesday |      +1 |      -6 |
| Wednesday |      +2 |      -5 |
|  Thursday |      +3 |      -4 |
|    Friday |      +4 |      -3 |
|  Saturday |      +5 |      -2 |
|    Sunday |      +6 |      -1 |

Note that, unless stated otherwise, the positive and negative offsets are interchangeable. A `-6` offset is harder to process mentally than a simple `+1` one, hence why most explanations below include both, when applicable.

---

## Finding the reference weekday for a given decade

You need to memorize a few things:

- Reference weekday for the year **2000** is **Tuesday**.
- Reference weekday for the year **1990** is **Wednesday**.
- Changing reference decades follows a **1-2-1-2** pattern. The direction and first step can be deduced from the two memorized reference decades.

When changing the reference decade, you have to follow the 1-2-1-2 pattern:

|    1950 |   1960 |     1970 |   1980 |      1990 |    2000 |   2010 |     2020 |     2030 |      2040 |
| :-----: | :----: | :------: | :----: | :-------: | :-----: | :----: | :------: | :------: | :-------: |
| Tuesday | Monday | Saturday | Friday | Wednesday | Tuesday | Sunday | Saturday | Thursday | Wednesday |

Notice how the reference weekday increases when going backwards through decades - this direction can be deduced from the two memorized **2000-Tuesday** and **1990-Wednesday** reference decades. Since the difference between those two memorized years is 1, the next step between decades changes by 2 instead: **1990-Wednesday** -> **1980-Friday**, with the next decade step changing by only 1 again. It works similarly when going up the other way, just mind the direction: **2000-Tuesday** -> **2010-Sunday**. This is how you can use the two reference decades and the **1-2-1-2** rule to figure out the reference decade that's the closest to your target year.

> [!Note]
> These rules can only be applied to the practical years range. See the "Extending the years range" section at the end for more information.

## Finding the reference weekday for a given year

You need to memorize a few more things:

- Leap years are divisible by **4** - this can be deduced from just the last two digits of the year. If the second-to-last digit is **even**, leap years end with a **0**, **4** and **8**. If the second-to-last digit is **odd**, leap years end with **2** and **6**.
- When counting the years up within a decade, the reference weekday changes up by **1**. When counting down, it changes down by **1**.
- When going up from a non-leap year to a leap year, the reference weekday changes up by **2** instead. Similarly, when going down from a leap year to a non-leap year, it changes down by **2** instead as well.

Once you have the reference decade that's close to the target year, you can quickly arrive at the reference weekday for a given year, by adding the amount of years in the last digit, to the amount of leap years encountered along the way, and taking a modulo 7 operation at the end. The result is an offset from the decade's reference weekday. Note the format is: `(years + leap) mod 7 = result`. Here's a few examples:

- 1986 -> 1980-Friday -> 1984 was leap -> `(6 + 1) mod 7 = 0` -> +0 offset from Friday -> Friday
- 1999 -> 1990-Wednesday -> 1992 and 1996 were leap -> `(9 + 2) mod 7 = 4` -> +4/-3 offset from Wednesday -> Sunday
- 2002 -> 2000-Tuesday -> no leap years -> `(2 + 0) mod 7 = 2` -> +2 offset from Tuesday -> Thursday
- 2014 -> 2010-Sunday -> 2012 was leap -> `(4 + 1) mod 7 = 5` -> +5/-2 offset from Sunday -> Friday
- 2026 -> 2020-Saturday -> 2024 was leap -> `(6 + 1) mod 7 = 0` -> +0 offset from Saturday -> Saturday

It's also possible to do this via subtraction, but with a catch - you need to watch out closely for the leap -> non-leap transition, as it's easy to forget to account for it here. For the example year 1999, you can use 2000-Tuesday as the starting point, and simply go back by 1 year. Accounting for the year 2000 being a leap and 1999 being non-leap, you need to subtract 2 instead of 1, so for the 2000-Tuesday reference, going back by 2 gives you Sunday immediately. Similarly, going 1 more year back requires you to only subtract 1 from the weekday offset (non-leap to non-leap transition), giving you Saturday.

### Speedup: Memorizing reference weekdays for a particular range of years

The fastest way of arriving at the reference weekday for a particular year, is done by simply memorizing a bunch of year-weekday pairs. You have a lot of flexibility here:

- You can memorize the reference decades only (1980, 1990, 2000, 2010, etc.), allowing you to bypass having to use the **1-2-1-2** rule and calculating the offset.
- You can memorize a particular range of years (1980-2020 for example), allowing you to skip all year-related offset calculations entirely.

The downside here is having to memorize a lot more information, rather than a bunch of rules explaining how to arrive at the answer. The upside is a huge increase in the weekday deduction speed, of course. Going this route is up for you to decide. Here are the pre-computed weekdays for the **1980-2020** years range:

| 1980      | 1981      | 1982      | 1983      | 1984      | 1985      | 1986      | 1987      | 1988      | 1989      | 1990      |
| :-------: | :-------: | :-------: | :-------: | :-------: | :-------: | :-------: | :-------: | :-------: | :-------: | :-------: |
| Friday    | Saturday  | Sunday    | Monday    | Wednesday | Thursday  | Friday    | Saturday  | Monday    | Tuesday   | Wednesday |
| 1990      | 1991      | 1992      | 1993      | 1994      | 1995      | 1996      | 1997      | 1998      | 1999      | 2000      |
| Wednesday | Thursday  | Saturday  | Sunday    | Monday    | Tuesday   | Thursday  | Friday    | Saturday  | Sunday    | Tuesday   |
| 2000      | 2001      | 2002      | 2003      | 2004      | 2005      | 2006      | 2007      | 2008      | 2009      | 2010      |
| Tuesday   | Wednesday | Thursday  | Friday    | Sunday    | Monday    | Tuesday   | Wednesday | Friday    | Saturday  | Sunday    |
| 2010      | 2011      | 2012      | 2013      | 2014      | 2015      | 2016      | 2017      | 2018      | 2019      | 2020      |
| Sunday    | Monday    | Wednesday | Thursday  | Friday    | Saturday  | Monday    | Tuesday   | Wednesday | Thursday  | Saturday  |

---

## Finding the weekday offset for a given month and day

This is the second step of the weekday-deduction process. The whole algorithm relies on the idea of date anchors: special day-month pairs, for which **the year's reference weekday is the same as the weekday of that date.**

There're a few more rules you need to memorize:

- For all even-numbered months, with **February (2)** as the only exception, the same-numbered day within the month falls on the reference weekday. This gives you **4/4**, **6/6**, **8/8**, **10/10** and **12/12** as anchor dates.
- For all other months in order, you need to memorize this sequence: **3-7-7_2-4-5-7**. This gives you **3/1**, **7/2**, **7/3**, **2/5**, **4/7**, **5/9** and **7/11** as anchors.
- The **5/9** and **7/11** anchors are reversible, which means that **9/5** and **11/7** can also be treated as anchors. The PI day (**14/3**) is also an anchor, as well as the last day of February (28th for non-leap years, 29th for leap years).

Remember: The year's reference weekday is the same as the weekday of each of those anchor dates. For example, if the reference weekday is a Monday, that means that **3/1**, **7/2**, **7/3**, **4/4**, **2/5**, **6/6**, **4/7**, **8/8**, **5/9**, **10/10**, **7/11** and **12/12** were all Mondays within that year. This gives you an anchor point within each of those months, from which you can calculate a weekday for any other day of a particular month, by subtracting the amount of days of the date, from the day offset given by the anchor, and then applying modulo **7** at the end. Here's a few examples:

- 14/3, year's reference weekday: Tuesday -> 7/3 anchor -> `14 - 7 mod 7 = 0` -> +0 offset from Tuesday -> Tuesday 
- 25/6, year's reference weekday: Friday -> 6/6 anchor -> `25 - 6 mod 7 = 5` -> +5/-2 offset from Friday -> Wednesday
- 18/9, year's reference weekday: Monday -> 12/9 anchor -> `18 - 12 mod 7 = 6` -> +6/-1 offset from Monday -> Sunday
- 21/12, year's reference weekday: Saturday -> 12/12 anchor -> `21 - 12 mod 7 = 2` -> +2 offset from Saturday -> Monday

### Speedup: Memorizing the offsets and anchor day-month pairs

Again, you can reduce the deduction time by memorizing offsets and anchor day-month pairs. Here are the reduced **(mod 7)** offsets for each month, in months' order:

```
3  0  0  4  2  6  4  1  5  3  0  5
```

And here's a breakdown per offset type, containing all anchor day-month pairs:

|                           |     |     |     |     |     |
| ------------------------: | :-: | :-: | :-: | :-: | :-: |
| February, March, November |   0 |   7 |  14 |  21 |  28 |
|                    August |   1 |   8 |  15 |  22 |  29 |
|                       May |   2 |   9 |  16 |  23 |  30 |
|          January, October |   3 |  10 |  17 |  24 |  31 |
|               April, July |   4 |  11 |  18 |  25 |     |
|       September, December |   5 |  12 |  19 |  26 |     |
|                      June |   6 |  13 |  20 |  27 |     |

## Final exception adjustment for leap years

As the very last step in the deduction process, one needs to test for a specific exception. For leap years that haven't passed through the 29th of February yet, you need to subtract 1 from the final result to obtain the correct weekday.

The general rules are simple:

- The year is a leap year.
- The month is either January or February.

For example, if the final deduced weekday would be a Saturday, for a leap year and either January or February as the month, the actually correct weekday deduction would be Friday instead.

## Putting it all together

Combining the three steps of figuring out the year's reference weekday, day-month offset and applying the final exception, you can finally arrive at the deduced weekday. Here's some examples:

- 14th of September, 1986 -> 1980-Friday -> +6+1=Friday -> 5/9 anchor -> `(14 - 5) mod 7 = 2` -> +2 offset from Friday -> Sunday
- 27th of March, 1997 -> 1990-Wednesday -> +7+2=Friday -> 7/3 anchor -> `(27 - 7) mod 7 = 6` -> +6/-1 offset from Friday -> Thursday
- 8th of February, 2004 -> 2000-Tuesday -> +4+1=Sunday -> 7/2 anchor -> `(8 - 7) mod 7 = 1` -> +1 offset, but final exception applies, so +0 offset from Sunday -> Sunday
- 19th of June, 2016 -> 2010-Sunday -> +6+2=Monday -> 6/6 anchor -> `(19 - 6) mod 7 = 6` -> +6/-1 offset from Monday -> Sunday
- 21st of November, 2026 -> 2020-Saturday -> +6+1=Saturday -> 7/11 anchor -> `(21 - 7) mod 7 = 0` -> +0 offset from Saturday -> Saturday

---

## Extending the years range

> [!NOTE]
> The Gregorian calendar had been introduced in **1582**, with different countries slowly adopting it over the following years. For this reason, deducing a weekday for years before **1600** won't really be historically accurate. If you're okay with ignoring this fact, the same math and logic still applies for years before **1600**.

To deduce the reference weekday for any year, there're a few more rules to remember:

- Years divisible by **400** (1600, 2000, 2400, etc.) have **Tuesday** as their reference weekday. You can consider those century anchors.
- Within each 400 years period, for each following century (+100, +200 or +300 from the century anchor), the sequence of reference weekdays is: **Sunday, Friday, Wednesday** (-2 offset for each). This lets you deduce the reference weekday for a given century.
- From here, you can apply the "odd + 11" method (see below) to obtain the reference weekday for the target year.

The "Odd + 11" method:

1. Start with the last two digits of the target year, and consider them your current number.
2. If the current number is odd: add 11, otherwise skip this step.
3. Divide the current number by 2 (this is a required step).
4. If the current number is odd: add 11, otherwise skip this step.
5. Compute `7 - (n mod 7)` (where `n` is the current number). This is equivalent to computing `n mod 7` and simply flipping the sign of the result.
6. The result is an offset from the century's reference weekday, that you can then use to obtain the reference weekday for the target year.

Here are some examples:

- 1673 -> 1600-Tuesday -> `(73 + 11) / 2 = 42` -> `42 mod 7 = 0` (no sign flip required) -> +0 offset from Tuesday -> Tuesday
- 1764 -> 1700-Sunday -> `64 / 2 = 32` -> `32 mod 7 = 4` (-4/+3 after sign flip) -> +3 offset from Sunday -> Wednesday
- 1847 -> 1800-Friday -> `(47 + 11) / 2 = 29` -> `(29 + 11) mod 7 = 5` (-5/+2 after sign flip) -> +2 offset from Friday -> Sunday
- 1929 -> 1900-Wednesday -> `(29 + 11) / 2 = 20` -> `20 mod 7 = 6` (-6/+1 after sign flip) -> +1 offset from Wednesday -> Thursday
- 2026 -> 2000-Tuesday -> `26 / 2 = 13` -> `(13 + 11) mod 7 = 3` (-3/+4 after sign flip) -> -3 offset from Tuesday -> Saturday

---

# Practice

The Python script lets you test your deduction skills in the 5 categories/modes explained below. Some technical details:

- There's currently no interface to change the script's configuration, other than by editing the code directly. This may be resolved in future versions of the script.
- More than one mode can be enabled at the same time. The weights specify how often each deduction type appears relative to the others. Setting the weight to zero prevents the type from appearing.
- There are three types of input methods: "general value", "offset" and "weekday". General value expects any positive or negative integer, offset expects only a range between -6 and 6, and weekday expects a name of a weekday.
- The weekday's name can be specified by typing only enough letters to distinguish it from the others. This is done to reduce the time wasted on typing in the answer.
- The "weekday" input method is currently disabled for `FULL_DATE` and `YEAR_ONLY` modes, and has been replaced by an alternative input method, that significantly speeds up weekday input. The keys ZXCVBNM (the lowest horizontal row of letters on a QWERTY keyboard) are mapped directly to the Monday-Sunday weekdays range. Simply pressing the corresponding key inputs the weekday immediately, without the need to press Enter afterwards.

### FULL_DATE: Deduce the weekday for a specific date

You're asked for the weekday of a specific date. Use the ZXCVBNM keys (mapped to the Monday-Sunday range) to answer.
The years are limited to the practical range only.
This allows you to practice deducing the weekday for a given date.

### YEAR_ONLY: Deduce the reference weekday for a specific year

You're asked for the reference weekday for a specific year. Use the ZXCVBNM keys (mapped to the Monday-Sunday range) to answer.
The years are limited to the practical range only.
This allows you to practice deducing the reference weekday for a given year.

### MONTH_ONLY: Deduce all day anchor offsets for a specific month

You're asked for all day anchor offsets for a specific month. Input all of them without spaces to answer.
Example answer for January: `310172431`, which corresponds to 3rd, 10th, 17th, 24th and 31st of January as anchors.
The initial `0` can be optionally omitted when inputting the answer for February, March and November.
This allows you to practice remembering anchor days within each month.

### DAY_MONTH_ONLY: Deduce the offset value for a specific month and day

You're asked for the offset value for a specific month and day. This can only range between -6 and 6, other values are rejected. A special "(leap)" text may sometimes appear to aid you when applying the final exception.
This allows you to practice deducing the offset value for a given month and day.

### OFFSET_WEEKDAY: Deduce the weekday for a given reference weekday and offset

You're asked for the weekday, given a reference weekday and an offset to it. For example, "+2  Saturday" results in "Monday" being the right answer.
This allows you to practice the final step of combining the offset deduced from a day and month combination, and the reference weekday deduced from the year.

### ODD_11: Deduce the offset value for a specific two-digit year ending

You're asked for the offset value for a specific two-digit year ending, using the "Odd + 11" method: see "Extending the years range" section for more information.
This allows you to practice the algorithm used in that method.
