# Bellabeat Wellness Intelligence Studio

I built this Streamlit dashboard to explore a simple question: **what can fitness tracker data tell us about everyday movement, sleep, and the kind of wellness support people might find useful?**

It brings together daily activity, hourly steps and calories, sleep, heart rate, and weight records. I also added a historical goal calculator, recommendations, and a SQL lab with 30 practice questions.

**[Explore the live dashboard](https://u6fhp6ny8mwa6lbgvwne5m.streamlit.app/)**

> This is an independent Bellabeat case study using third-party Fitbit data from **12 April to 12 May 2016**. It is not Bellabeat customer data or medical advice.

## Why I built it

One average can make a group look more similar than it really is. I wanted to see how movement changes across people and days, whether a fixed 10,000-step goal fits the records, and how missing sleep data affects the story. The goal is to turn those observations into ideas Bellabeat could test with its own users.

## What I found

With all dates, participants, and day types selected, the dashboard covers **33 anonymous device IDs, 940 participant-days, and 22,099 participant-hours**.

| Finding | Full-sample result | What it means |
| --- | ---: | --- |
| Average daily steps | 7,638 | A useful starting point, but it hides wide variation. |
| Days below 5,000 steps | 303 / 940 (32.2%) | Many days are well below the common 10k goal. |
| Days reaching 10,000 steps | 303 / 940 (32.2%) | An equally large share reaches that goal. |
| Days reaching 8,000 steps | 46.1% | Historical completion changes with the chosen target. |
| Days with sleep recorded | 410 / 940 (43.6%) | More than half of the daily rows lack sleep duration. |
| Average recorded sleep | 7.0 hours | This covers observed nights only. |
| Peak hour by mean steps | 18:00 | A timing idea to test, not a proven best reminder time. |

The contrast in step counts stood out to me: **32.2% of days are below 5,000 steps, while another 32.2% reach 10,000**. This is why I would test goals based on a person's recent activity instead of assuming one target suits everyone. All figures update when you change the dashboard filters.

## Explore the dashboard

1. **Project brief** introduces the question, sources, and limits of the sample.
2. **The pulse** brings the main KPIs, step trend, and activity mix together.
3. **Movement** compares weekly patterns, activity intensity, steps, calories, and step distributions.
4. **Sleep** explores duration and makes missing sleep records visible.
5. **Daily rhythm** shows when activity happens through the day and week.
6. **Body signals** shows the heart-rate and weight records that are available.
7. **Audience explorer** compares participant averages, goal completion, and consistency.
8. **Goals & strategy** lets you set step, active-minute, and sleep targets against recorded history.
9. **Findings & actions** connects patterns to measurable product experiments.
10. **SQL Analysis** offers 30 intermediate and advanced SQLite questions.

The sidebar filters by **date range, anonymous participant ID, and weekday/weekend**. Those choices carry through the charts, calculator, SQL tables, and CSV downloads. The participant and goal pages also have their own controls.

## How I prepared the data

I used daily activity as the base, with **one row per participant and date**. Sleep and weight logs were matched by participant and date. Heart-rate readings and hourly data were summarized before joining, so the merge would not multiply daily rows. I kept an hourly activity table for the time-of-day analysis.

| Source | Used for | Full-sample coverage |
| --- | --- | --- |
| Daily activity | Steps, active minutes, distance, total calories | 940 days |
| Sleep | Duration, efficiency, recorded-night goals | 410 days |
| Hourly steps and calories | Activity through the day | 22,099 hours |
| Weight | Optional weight and recorded BMI | 67 days; 8 people |
| Heart rate | Available daily summaries | 334 days; 14 people |

The combined CSV was prepared from the project's six source streams. The app checks the columns it needs and removes duplicate participant-date and participant-hour keys in its analysis view. Missing optional measurements stay missing; they are never counted as zero.

## Run the project locally

Arrange the files like this:

```text
your-project/
├── app.py
├── sql_lab.py
├── requirements.txt
├── Cleaned Data/                  # Cleaned_Data/ or data/ also works
│   ├── fitness_all_six_daily.csv
│   └── hourly_activity.csv
└── Images/                        # images/ or beside app.py also works
    ├── muscle anatomy.png         # muscle_anatomy.png or anatomy.png also works
    ├── movement.png
    ├── sleep.png
    ├── sql.jpg
    └── Heart Beat.jpg             # H BIt.jpg also works
```

The two CSV filenames must match exactly. Images are optional: the app still runs without them, although their visuals will not appear. These illustrations were supplied for the project; the app does not generate them.

Create a virtual environment:

```bash
python -m venv .venv
```

On **Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On **macOS or Linux**:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run app.py
```

The terminal will show a local URL, usually `http://localhost:8501`. Python's built-in `sqlite3` module runs the SQL lab.

## Try the SQL lab

The lab creates temporary SQLite tables from the **currently filtered data**: `fitness_all_six_daily` for participant-days and `hourly_activity` for participant-hours. `daily_wellness` is an alias for the daily table.

Choose a topic and difficulty, look at the table columns, write a read-only `SELECT` query, and compare your result with a reference answer. The app displays up to 500 rows and lets you download the result.

```sql
SELECT DayType,
       COUNT(*) AS recorded_days,
       ROUND(AVG(TotalSteps), 0) AS avg_steps
FROM fitness_all_six_daily
GROUP BY DayType;
```

## Ideas worth testing

1. **A personal step goal:** Compare a target based on recent steps with a fixed goal. Measure four-week activity, completion, and reminder opt-outs.
2. **A sleep summary with honest coverage:** Show a weekly summary only when enough nights were recorded, and tell users how complete it is.
3. **Better timing for optional prompts:** Compare messages near a user's usual active window with a fixed send time, while watching for notification fatigue.
4. **Clear choices around body measurements:** Explain available weight and heart-rate records, and let people opt in without making health claims.

These are **experiments to consider**, not features proven to work by this dataset.

## What the data cannot tell us

This is a small observational Fitbit sample from 2016. It has no Bellabeat customer IDs, demographics, purchases, or campaign outcomes, so I cannot use it to claim what Bellabeat customers want or how a product change would perform. Sleep, heart-rate, weight, and hourly data have different coverage. Same-date steps and sleep do not establish cause and effect, and total calories include baseline expenditure.

The calculator reports how often a target was met **in the selected history**; it is not a forecast. Its default last-14-dates window also differs from the full-sample figures above.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit pages, filters, charts, and goal calculator |
| `sql_lab.py` | SQL questions and read-only query runner |
| `requirements.txt` | Python packages needed to run the app |
| `Cleaned Data/fitness_all_six_daily.csv` | Combined daily analysis table |
| `Cleaned Data/hourly_activity.csv` | Hourly movement table |
| `client_storytelling.md` | Page-by-page presentation script |
| `Bellabeat_Wellness_Project_Report.pdf` | Full project report |

## About me

I'm **Ankan Chowdhury**, an aspiring data analyst interested in turning clean data into clear business decisions. This project brings together Python, SQL, dashboard design, and storytelling around a real analysis question.
