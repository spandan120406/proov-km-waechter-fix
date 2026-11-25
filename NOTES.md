# What I checked, and what the agent got wrong

## What the agent got wrong
Two things stood out on this job.

The first was the MILES_PER_KM constant in fleet_utils.py. The original value was 1.609, and the agent correctly identified it as wrong — but I double-checked the direction myself before accepting the fix. The correct conversion is km × 0.621371 = miles (because one mile is 1.609 km, not the other way around). The nightly UK report had been printing roughly 2.6× the real distance for years without anyone noticing, because no test covered the output of km_to_miles.

The second was subtler: when the agent first described the needs_service missing-reading fix, it said "default to 0" was the problem and proposed defaulting to the odometer value instead. That is correct, but I traced through the logic myself to confirm: if last_service_km is absent and we default to car["odometer"], then km_since = odometer - odometer = 0, so wear = 0% and the car is never falsely flagged. The reasoning holds. I would not have caught a wrong fix here unless I had done that trace manually.


## What I checked before I accepted its work
Before accepting any change I ran two checks back to back:

python -m pytest test_km_wachter.py test_fleet_report.py -v — confirmed all four tests pass, including the new test_summary_does_not_crash_on_missing_reading test that was added as part of the task. I looked at each test name and matched it to the bug it covers so I was sure the tests were actually testing the right things, not just passing vacuously.

python verify.py — this is the acceptance script that checks eleven concrete requirements independently of the test suite. I read each PASS line and matched it to a specific code change:

"Wear is no longer floored to 0" proves the // → / fix in wear_percent().
"The nearly-worn car is flagged" proves VOS-4471 at 14,900 km is now caught.
"A missing reading is handled" proves VOS-7788 with no last-service km is no longer falsely flagged.
"The 15000 km / 80% rules are untouched" proves the constants were not accidentally changed.
"The km-to-miles conversion is fixed" proves the inverted MILES_PER_KM was corrected.
"The average wear is correct" proves the // floor division in fleet_summary was fixed.
"The nightly report no longer crashes" proves car_wear() no longer raises KeyError.
The only FAIL that remained was NOTES.md, which is intentionally a human-authored section.



## What the data actually said
The obvious assumption going in was that older cars with higher total mileage would break down more. The data does not support that at all.

After splitting the 120 cars into the group that broke down (26 cars) and the group that did not (94 cars) and comparing every column's mean between the two groups, the results were clear:

odometer_km (total lifetime mileage): group means of 53,448 vs 53,302 — a 0.3% difference and a correlation of r = +0.002 with breakdown. Essentially zero signal. A car with 100,000 km on the clock is no more likely to break than one with 10,000 km in this dataset.

age_years: group means of 5.88 vs 5.89 — a -0.2% difference and r = -0.001. Completely flat. Age predicts nothing here.

The three columns that genuinely separate the two groups are:

km_since_service — mean 11,678 km for broken cars vs 7,261 km for safe cars (+61% higher), r = +0.404. This is the strongest predictor by far. Cars that are deep into their current service window — not cars with high total mileage — are the ones that break down. This is the column that drives the 80% service rule, and the data confirms it is the right one.

avg_daily_km — mean 160 km/day for broken cars vs 131 km/day for safe cars (+22% higher), r = +0.252. Cars being driven harder each day accumulate wear faster and fail more often.

load_factor — mean 0.60 for broken cars vs 0.51 for safe cars (+19% higher), r = +0.215. Carrying heavier loads puts more stress on components regardless of distance travelled.

The risk score was built from these three columns only, min-max scaled to put them on a common footing, then weighted by correlation strength (0.50 / 0.30 / 0.20). The result: 8 of the 10 highest-scoring cars actually broke down — an 80% hit rate against a 22% fleet-wide base rate. The mean risk score for cars that broke down was 62.5 vs 41.7 for cars that did not, a gap of +20.8 points, which confirms the score is carrying real predictive signal and not just noise.
