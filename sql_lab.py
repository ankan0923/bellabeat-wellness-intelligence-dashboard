"""Curated SQLite exercises and a limited, read-only query runner."""
import sqlite3
import time
import pandas as pd


def q(level, category, question, hint, solution):
    return dict(level=level, category=category, question=question, hint=hint, solution=solution.strip())

QUESTIONS = [
    q("Intermediate", "Data quality", "Count participant-days, unique participants, and observed dates.", "Use COUNT(*) and COUNT(DISTINCT ...).", """SELECT COUNT(*) AS participant_days, COUNT(DISTINCT Id) AS participants,
COUNT(DISTINCT Date) AS dates FROM daily_wellness;"""),
    q("Intermediate", "Data quality", "Find how many days have sleep data and the reporting percentage.", "COUNT(SleepHours) ignores NULL; divide by COUNT(*).", """SELECT COUNT(SleepHours) AS sleep_days, COUNT(*) AS observed_days,
ROUND(100.0 * COUNT(SleepHours) / COUNT(*), 1) AS coverage_pct FROM daily_wellness;"""),
    q("Intermediate", "Movement", "Show average steps and active minutes by weekday in calendar order.", "Group by DayName and sort using DayNumber.", """SELECT DayName, ROUND(AVG(TotalSteps),0) AS avg_steps,
ROUND(AVG(TotalActiveMinutes),0) AS avg_active_minutes, COUNT(*) AS days
FROM daily_wellness GROUP BY DayNumber, DayName ORDER BY DayNumber;"""),
    q("Intermediate", "Movement", "Compare weekday and weekend averages for steps, distance, and active minutes.", "Use DayType and AVG.", """SELECT DayType, COUNT(*) AS days, ROUND(AVG(TotalSteps),0) AS avg_steps,
ROUND(AVG(TotalDistance),2) AS avg_km,
ROUND(AVG(TotalActiveMinutes),0) AS avg_active_minutes
FROM daily_wellness GROUP BY DayType;"""),
    q("Intermediate", "Movement", "Find the 10 highest-step participant-days with dates and distance.", "Sort TotalSteps descending and LIMIT 10.", """SELECT Id, Date, TotalSteps, TotalDistance
FROM daily_wellness ORDER BY TotalSteps DESC LIMIT 10;"""),
    q("Intermediate", "Goals", "Calculate the 10,000-step goal attainment rate by day type.", "Use SUM(CASE WHEN ...) over COUNT(*).", """SELECT DayType, COUNT(*) AS days,
SUM(CASE WHEN TotalSteps >= 10000 THEN 1 ELSE 0 END) AS goal_days,
ROUND(100.0 * SUM(CASE WHEN TotalSteps >= 10000 THEN 1 ELSE 0 END)/COUNT(*),1) AS goal_rate_pct
FROM daily_wellness GROUP BY DayType;"""),
    q("Intermediate", "Sleep", "Compare average sleep hours and efficiency by weekday, using observed sleep days only.", "Exclude NULL SleepHours.", """SELECT DayName, COUNT(*) AS recorded_nights,
ROUND(AVG(SleepHours),2) AS avg_sleep_hours,
ROUND(AVG(SleepEfficiency),1) AS avg_efficiency_pct
FROM daily_wellness WHERE SleepHours IS NOT NULL
GROUP BY DayNumber, DayName ORDER BY DayNumber;"""),
    q("Intermediate", "Sleep", "Count recorded nights in under 6, 6–7, 7–9, and 9+ hour bands.", "Use a CASE expression and filter missing sleep.", """SELECT CASE WHEN SleepHours < 6 THEN 'Under 6h'
WHEN SleepHours < 7 THEN '6–7h' WHEN SleepHours < 9 THEN '7–9h'
ELSE '9+h' END AS sleep_band, COUNT(*) AS nights
FROM daily_wellness WHERE SleepHours IS NOT NULL
GROUP BY sleep_band ORDER BY MIN(SleepHours);"""),
    q("Intermediate", "Movement", "Find participants averaging at least 10,000 steps over at least 10 observed days.", "Use GROUP BY Id with two HAVING conditions.", """SELECT Id, COUNT(*) AS observed_days, ROUND(AVG(TotalSteps),0) AS avg_steps
FROM daily_wellness GROUP BY Id
HAVING COUNT(*) >= 10 AND AVG(TotalSteps) >= 10000
ORDER BY avg_steps DESC;"""),
    q("Intermediate", "Hourly rhythm", "Find the five hours with the highest average steps, including their record counts.", "Group by Hour, not ActivityHour.", """SELECT Hour, COUNT(*) AS recorded_hours, ROUND(AVG(StepTotal),0) AS avg_steps
FROM hourly_activity GROUP BY Hour ORDER BY avg_steps DESC LIMIT 5;"""),
    q("Intermediate", "Hourly rhythm", "Compare hourly steps by time period and day type.", "Group on TimePeriod and DayType.", """SELECT TimePeriod, DayType, COUNT(*) AS records,
ROUND(AVG(StepTotal),0) AS avg_steps
FROM hourly_activity GROUP BY TimePeriod, DayType
ORDER BY TimePeriod, DayType;"""),
    q("Intermediate", "Data quality", "Identify any duplicate participant-date keys in the daily table.", "Group by Id and Date; HAVING COUNT(*) > 1.", """SELECT Id, Date, COUNT(*) AS row_count
FROM daily_wellness GROUP BY Id, Date HAVING COUNT(*) > 1;"""),
    q("Intermediate", "Data quality", "Count days with fewer than 10 hours of wear time, by day type.", "WearTimeMinutes is measured in minutes.", """SELECT DayType, COUNT(*) AS days_under_10h
FROM daily_wellness WHERE WearTimeMinutes < 600
GROUP BY DayType ORDER BY days_under_10h DESC;"""),
    q("Intermediate", "Weight", "Count days with a recorded weight and BMI, and the participants represented.", "COUNT(column) ignores NULL; these logs are sparse.", """SELECT COUNT(*) AS activity_days,
COUNT(WeightKg) AS weight_days, COUNT(BMI) AS bmi_days,
COUNT(DISTINCT CASE WHEN WeightKg IS NOT NULL THEN Id END) AS participants_with_weight
FROM fitness_all_six_daily;"""),
    q("Intermediate", "Heart rate", "Find heart-rate reporting coverage and the total number of recorded readings.", "COUNT(HeartRateMean) counts days with a summary; SUM(HeartRateReadings) counts readings.", """SELECT COUNT(*) AS activity_days, COUNT(HeartRateMean) AS heart_rate_days,
ROUND(100.0*COUNT(HeartRateMean)/COUNT(*),1) AS coverage_pct,
SUM(HeartRateReadings) AS readings
FROM fitness_all_six_daily;"""),
    q("Advanced", "Window functions", "Rank each participant's days from most to least steps, and return their top three.", "ROW_NUMBER() within each Id.", """WITH ranked AS (
 SELECT Id, Date, TotalSteps,
 ROW_NUMBER() OVER (PARTITION BY Id ORDER BY TotalSteps DESC, Date) AS step_rank
 FROM daily_wellness)
SELECT * FROM ranked WHERE step_rank <= 3 ORDER BY Id, step_rank;"""),
    q("Advanced", "Window functions", "Calculate a seven-observation rolling average of steps for each participant.", "Use ROWS BETWEEN 6 PRECEDING AND CURRENT ROW; first rows have fewer than seven observations.", """SELECT Id, Date, TotalSteps,
ROUND(AVG(TotalSteps) OVER (PARTITION BY Id ORDER BY Date
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),0) AS rolling_7_observed_days
FROM daily_wellness ORDER BY Id, Date;"""),
    q("Advanced", "Window functions", "Show each participant's day-over-day change in steps on consecutive recorded dates.", "Use LAG, then require a one-day date difference.", """WITH prev AS (
 SELECT Id, Date, TotalSteps,
 LAG(Date) OVER (PARTITION BY Id ORDER BY Date) AS previous_date,
 LAG(TotalSteps) OVER (PARTITION BY Id ORDER BY Date) AS previous_steps
 FROM daily_wellness)
SELECT Id, Date, TotalSteps, previous_steps,
TotalSteps-previous_steps AS step_change
FROM prev WHERE julianday(Date)-julianday(previous_date)=1
ORDER BY Id, Date;"""),
    q("Advanced", "Window functions", "Find the longest consecutive run of 10,000-step days per participant.", "Use row-number islands on qualifying days, then group each run.", """WITH goals AS (
 SELECT Id, Date, CAST(julianday(Date) AS INTEGER) -
 ROW_NUMBER() OVER (PARTITION BY Id ORDER BY Date) AS run_key
 FROM daily_wellness WHERE TotalSteps >= 10000),
runs AS (SELECT Id, MIN(Date) AS run_start, MAX(Date) AS run_end,
COUNT(*) AS streak_days FROM goals GROUP BY Id, run_key),
ranked AS (SELECT *, ROW_NUMBER() OVER
(PARTITION BY Id ORDER BY streak_days DESC, run_start) AS rn FROM runs)
SELECT Id, run_start, run_end, streak_days FROM ranked WHERE rn=1
ORDER BY streak_days DESC, Id;"""),
    q("Advanced", "Segmentation", "Segment participants by mean steps: under 5k, 5k–10k, and 10k+, requiring at least 10 days.", "Aggregate per Id first, then label and summarize.", """WITH people AS (
 SELECT Id, COUNT(*) AS days, AVG(TotalSteps) AS avg_steps
 FROM daily_wellness GROUP BY Id HAVING COUNT(*) >= 10),
segments AS (SELECT Id, days, avg_steps,
CASE WHEN avg_steps < 5000 THEN 'Under 5k'
WHEN avg_steps < 10000 THEN '5k–10k' ELSE '10k+' END AS segment FROM people)
SELECT segment, COUNT(*) AS participants, ROUND(AVG(avg_steps),0) AS mean_participant_steps
FROM segments GROUP BY segment ORDER BY mean_participant_steps;"""),
    q("Advanced", "Segmentation", "Compare sleep coverage and average sleep by participant movement segment.", "Build segments at participant level, then join back to daily records.", """WITH people AS (
 SELECT Id, AVG(TotalSteps) AS avg_steps FROM daily_wellness
 GROUP BY Id HAVING COUNT(*) >= 10),
segments AS (SELECT Id, CASE WHEN avg_steps < 5000 THEN 'Under 5k'
 WHEN avg_steps < 10000 THEN '5k–10k' ELSE '10k+' END AS segment FROM people)
SELECT s.segment, COUNT(DISTINCT d.Id) AS participants,
COUNT(*) AS days, COUNT(d.SleepHours) AS sleep_days,
ROUND(100.0*COUNT(d.SleepHours)/COUNT(*),1) AS coverage_pct,
ROUND(AVG(d.SleepHours),2) AS avg_observed_sleep_h
FROM daily_wellness d JOIN segments s ON d.Id=s.Id
GROUP BY s.segment ORDER BY s.segment;"""),
    q("Advanced", "Sleep", "On consecutive recorded days, compare steps after nights with under 7 versus at least 7 hours of sleep.", "Use LAG(SleepHours); align only consecutive dates. This is descriptive.", """WITH prior AS (
 SELECT Id, Date, TotalSteps,
 LAG(Date) OVER (PARTITION BY Id ORDER BY Date) AS prior_date,
 LAG(SleepHours) OVER (PARTITION BY Id ORDER BY Date) AS prior_sleep_h
 FROM daily_wellness)
SELECT CASE WHEN prior_sleep_h < 7 THEN 'Under 7h' ELSE '7h+' END AS prior_sleep_band,
COUNT(*) AS days, ROUND(AVG(TotalSteps),0) AS avg_next_day_steps
FROM prior WHERE prior_sleep_h IS NOT NULL
AND julianday(Date)-julianday(prior_date)=1
GROUP BY prior_sleep_band;"""),
    q("Advanced", "Hourly rhythm", "Find the peak step hour separately for each weekday.", "Aggregate first, then rank within DayName.", """WITH averages AS (
 SELECT DayName, DayNumber, Hour, COUNT(*) AS records,
 AVG(StepTotal) AS avg_steps FROM hourly_activity
 GROUP BY DayName, DayNumber, Hour),
ranked AS (SELECT *, ROW_NUMBER() OVER
(PARTITION BY DayName ORDER BY avg_steps DESC, Hour) AS rn FROM averages)
SELECT DayName, Hour, records, ROUND(avg_steps,0) AS avg_steps
FROM ranked WHERE rn=1 ORDER BY DayNumber;"""),
    q("Advanced", "Hourly rhythm", "For each participant, find the hour contributing the largest share of their recorded steps.", "Sum steps per participant-hour and divide by the participant total.", """WITH per_hour AS (
 SELECT Id, Hour, SUM(StepTotal) AS steps FROM hourly_activity GROUP BY Id, Hour),
ranked AS (SELECT Id, Hour, steps,
ROUND(100.0*steps/NULLIF(SUM(steps) OVER (PARTITION BY Id),0),1) AS share_pct,
ROW_NUMBER() OVER (PARTITION BY Id ORDER BY steps DESC, Hour) AS rn FROM per_hour)
SELECT Id, Hour AS peak_hour, steps, share_pct FROM ranked WHERE rn=1 ORDER BY Id;"""),
    q("Advanced", "Validation", "Compare daily step totals with summed hourly steps for matched participant-dates.", "Aggregate hourly data before joining; do not multiply daily rows.", """WITH hourly_day AS (
 SELECT Id, Date, SUM(StepTotal) AS hourly_steps, COUNT(*) AS hours
 FROM hourly_activity GROUP BY Id, Date)
SELECT d.Id, d.Date, d.TotalSteps AS daily_steps, h.hourly_steps,
d.TotalSteps-h.hourly_steps AS difference, h.hours
FROM daily_wellness d JOIN hourly_day h ON d.Id=h.Id AND d.Date=h.Date
WHERE d.TotalSteps<>h.hourly_steps ORDER BY ABS(d.TotalSteps-h.hourly_steps) DESC LIMIT 25;"""),
    q("Advanced", "Validation", "Compare the stored daily hourly-step summary with a fresh hourly aggregation, including coverage.", "Join an hourly aggregate to the six-source daily table on Id and Date.", """WITH hourly_day AS (
 SELECT Id, Date, SUM(StepTotal) AS summed_steps, COUNT(*) AS observed_hours
 FROM hourly_activity GROUP BY Id, Date)
SELECT COUNT(*) AS matched_days,
SUM(CASE WHEN d.HourlyStepsTotal=h.summed_steps THEN 1 ELSE 0 END) AS summary_matches,
ROUND(AVG(h.observed_hours),1) AS mean_observed_hours,
SUM(CASE WHEN d.TotalSteps=h.summed_steps THEN 1 ELSE 0 END) AS daily_step_matches
FROM fitness_all_six_daily d JOIN hourly_day h ON d.Id=h.Id AND d.Date=h.Date;"""),
    q("Advanced", "Behavior", "Compare each participant's weekday and weekend mean steps when both are observed.", "Conditional aggregation with HAVING for both groups.", """SELECT Id,
ROUND(AVG(CASE WHEN DayType='Weekday' THEN TotalSteps END),0) AS weekday_steps,
ROUND(AVG(CASE WHEN DayType='Weekend' THEN TotalSteps END),0) AS weekend_steps,
ROUND(AVG(CASE WHEN DayType='Weekend' THEN TotalSteps END)-
AVG(CASE WHEN DayType='Weekday' THEN TotalSteps END),0) AS weekend_difference
FROM daily_wellness GROUP BY Id
HAVING COUNT(CASE WHEN DayType='Weekday' THEN 1 END)>0
AND COUNT(CASE WHEN DayType='Weekend' THEN 1 END)>0
ORDER BY weekend_difference DESC;"""),
    q("Advanced", "Behavior", "Find each participant's longest consecutive run of days with any recorded steps.", "Use date-minus-row-number islands after filtering positive steps.", """WITH active AS (
 SELECT Id, Date, CAST(julianday(Date) AS INTEGER)-
 ROW_NUMBER() OVER (PARTITION BY Id ORDER BY Date) AS grp
 FROM daily_wellness WHERE TotalSteps>0),
runs AS (SELECT Id, MIN(Date) AS start_date, MAX(Date) AS end_date,
COUNT(*) AS run_days FROM active GROUP BY Id, grp),
ranked AS (SELECT *, ROW_NUMBER() OVER
(PARTITION BY Id ORDER BY run_days DESC, start_date) AS rn FROM runs)
SELECT Id, start_date, end_date, run_days FROM ranked WHERE rn=1 ORDER BY run_days DESC;"""),
    q("Advanced", "Heart rate", "For participants with at least five heart-rate days, compare their mean observed heart rate and mean daily steps.", "Aggregate both measures at the participant level; heart-rate means use only observed days.", """SELECT Id, COUNT(*) AS activity_days,
COUNT(HeartRateMean) AS heart_rate_days,
ROUND(AVG(HeartRateMean),1) AS mean_recorded_bpm,
ROUND(AVG(TotalSteps),0) AS mean_daily_steps
FROM fitness_all_six_daily GROUP BY Id
HAVING COUNT(HeartRateMean)>=5 ORDER BY mean_recorded_bpm DESC;"""),
    q("Advanced", "Marketing", "Estimate the share of eligible participants in each movement segment and their goal rates.", "First require 10 observed days, then join the segment back to daily data.", """WITH people AS (
 SELECT Id, AVG(TotalSteps) AS avg_steps FROM daily_wellness
 GROUP BY Id HAVING COUNT(*)>=10),
segments AS (SELECT Id, CASE WHEN avg_steps<5000 THEN 'Under 5k'
WHEN avg_steps<10000 THEN '5k–10k' ELSE '10k+' END AS segment FROM people),
results AS (SELECT s.segment, COUNT(DISTINCT s.Id) AS participants,
COUNT(*) AS days, SUM(CASE WHEN d.TotalSteps>=10000 THEN 1 ELSE 0 END) AS goal_days
FROM segments s JOIN daily_wellness d ON s.Id=d.Id GROUP BY s.segment)
SELECT segment, participants,
ROUND(100.0*participants/SUM(participants) OVER (),1) AS participant_share_pct,
ROUND(100.0*goal_days/days,1) AS goal_rate_pct
FROM results ORDER BY participant_share_pct DESC;"""),
]
assert len(QUESTIONS)==30


def make_connection(daily: pd.DataFrame, hourly: pd.DataFrame) -> sqlite3.Connection:
    conn=sqlite3.connect(":memory:")
    daily.to_sql("fitness_all_six_daily",conn,index=False,if_exists="replace")
    hourly.to_sql("hourly_activity",conn,index=False,if_exists="replace")
    conn.execute("CREATE VIEW daily_wellness AS SELECT * FROM fitness_all_six_daily")
    conn.execute("CREATE INDEX daily_key ON fitness_all_six_daily(Id, Date)")
    conn.execute("CREATE INDEX hourly_key ON hourly_activity(Id, Date, Hour)")
    return conn


def execute_readonly(conn: sqlite3.Connection, query: str, max_rows=500, max_seconds=5.0):
    query=query.strip()
    if not query or not query.lstrip().upper().startswith(("SELECT", "WITH")):
        raise ValueError("Enter a SELECT query or a WITH query ending in SELECT.")
    # SQLite authorizer blocks modifications and access to hidden schema tables.
    allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,
             sqlite3.SQLITE_RECURSIVE,sqlite3.SQLITE_SAVEPOINT}
    def authorize(action,arg1,arg2,dbname,source):
        if action==sqlite3.SQLITE_READ and (arg1 or "").lower().startswith("sqlite_"):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
    deadline=time.monotonic()+max_seconds
    conn.set_authorizer(authorize)
    conn.set_progress_handler(lambda: 1 if time.monotonic()>deadline else 0,10000)
    try:
        cur=conn.execute(query)
        if cur.description is None: raise ValueError("The query must return a result table.")
        columns=[col[0] for col in cur.description]
        rows=cur.fetchmany(max_rows+1)
        return pd.DataFrame(rows[:max_rows],columns=columns),len(rows)>max_rows
    finally:
        conn.set_authorizer(None)
        conn.set_progress_handler(None,0)
