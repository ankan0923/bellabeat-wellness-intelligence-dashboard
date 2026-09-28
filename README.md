# Bellabeat Wellness Intelligence Studio

An interactive Streamlit case study that turns Fitbit activity, sleep, hourly movement, heart-rate, and weight records into a practical Bellabeat product research brief. The app combines visual exploration, a historical fitness goal calculator, recommendations, and a 30-question SQL analysis lab.

> **Scope:** This is third-party Fitbit data from **12 April to 12 May 2016**, not Bellabeat customer data. The findings generate ideas to test; they do not establish product impact or provide medical advice.

## Project objective

Explore how movement differs across days and participants, identify gaps in sleep reporting, and propose measurable, optional wellness features. The central question is: **Could personal activity baselines and clearer data coverage make wellness feedback more useful than a single fixed goal?**

## Headline findings

The unfiltered dashboard contains **33 anonymous participants**, **940 participant-days**, and **22,099 participant-hours**.

| Finding | Full-sample result | Interpretation |
| --- | ---: | --- |
| Mean daily steps | 7,638 | The overall mean conceals substantial variation. |
| Days below 5,000 steps | 303 / 940 (32.2%) | A sizable lower-activity group of days. |
| Days at or above 10,000 steps | 303 / 940 (32.2%) | The same share reaches the common fixed goal. |
| Days at or above 8,000 steps | 46.1% | Historical attainment changes when the threshold changes. |
| Sleep reporting | 410 / 940 days (43.6%) | Sleep summaries apply only to recorded nights. |
| Mean sleep on recorded nights | 7.0 hours | Missing nights are excluded, not treated as zero. |
| Peak observed step hour | 18:00 | A possible window to investigate, not a proven best prompt time. |

These figures change when a date, participant, or day-type filter is applied.

## Dashboard pages

1. **Project brief:** Business question, preparation workflow, source coverage, and sample limits.
2. **The pulse:** Executive KPIs, daily step trend and variation, and activity-band composition.
3. **Movement:** Weekly step patterns, weekday/weekend goal gauges, intensity mix, step-calorie relationships, and step distributions.
4. **Sleep:** Duration distribution, duration doughnut, reporting coverage by activity band and date, and steps-versus-sleep view.
5. **Daily rhythm:** Hourly movement, separately indexed steps and calories, a day-hour heatmap, and time-period comparison.
6. **Body signals:** Available heart-rate and weight timelines with clear coverage counts.
7. **Audience explorer:** Participant-level movement, goal attainment, consistency, and three movement-group doughnuts.
8. **Goals & strategy:** Historical step, active-minute, and sleep target scenarios; baseline windows; goal comparison; and test ideas.
9. **Findings & actions:** Evidence, proposed experiments, success measures, and guardrails.
10. **SQL Analysis:** 30 intermediate and advanced SQLite challenges with hints, an editor, reference queries, and downloadable results.

The sidebar filters by **date range**, **anonymous device IDs**, and **weekday/weekend**. The same selection feeds the charts, calculator, SQL tables, and daily/hourly downloads. The Audience explorer also has a minimum-recorded-days slider; the calculator has its own participant, baseline-window, and goal controls.

## Data preparation

The merged daily file represents one row per participant and date. Daily activity is the base table; sleep and weight are matched on participant/date. Heart-rate and hourly records are aggregated before the daily join to avoid multiplying rows. The hourly activity file remains separate to preserve the hour-level analysis.

| Input in the analytical view | Main use | Full-sample coverage |
| --- | --- | --- |
| Daily activity | Steps, active minutes, distance, total calories | 940 days |
| Sleep | Duration, efficiency, observed-night goals | 410 days |
| Hourly steps and calories | Hourly patterns | 22,099 hours |
| Weight | Optional weight and recorded BMI | 67 days; 8 participants |
| Heart rate | Available daily summaries | 334 days; 14 participants |

The combined CSV was prepared from the project's six source streams. The app checks required columns and drops duplicate participant-date or participant-hour keys in its loaded analysis view. Missing optional measurements remain missing.

## Run locally

### 1. Arrange the files

```text
your-project/
├── app.py
├── sql_lab.py
├── Cleaned_Data/
│   ├── fitness_all_six_daily.csv
│   └── hourly_activity.csv
└── images/                         # You may instead put images beside app.py
    ├── muscle_anatomy.png           # anatomy.png is also accepted
    ├── movement.png
    ├── sleep.png
    ├── sql.jpg                      # optional SQL page banner
    └── H BIt.jpg                    # optional Body signals banner
```

The three PNGs are required by the current `app.py`. The two JPG banners are optional. Use the provided image files; the app does not generate these assets. If your anatomy file is named `anatomy.png`, you can keep that name. File names and capitalization for the other images should match the tree above.

The CSV filenames must be exactly `fitness_all_six_daily.csv` and `hourly_activity.csv`. The app also accepts a `data/` directory or CSVs beside `app.py`, but `Cleaned_Data/` is the recommended layout.

### 2. Install dependencies

From a terminal in `your-project`:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install streamlit pandas numpy plotly
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install streamlit pandas numpy plotly
```

### 3. Launch

```bash
streamlit run app.py
```

Open the local address shown in the terminal, usually `http://localhost:8501`. `sqlite3`, used by the SQL lab, is included with standard Python installations.

## SQL practice

The **SQL Analysis** page creates a temporary SQLite connection from the *currently filtered* data:

- `fitness_all_six_daily`: one row per selected participant-day;
- `hourly_activity`: selected participant-hours;
- `daily_wellness`: a view alias for the daily table.

Choose difficulty and topic, inspect the schema, write a read-only `SELECT` query, run it, and compare your result with a reference solution. Up to 500 rows display in the app; results can be downloaded as CSV. This lab is educational and uses the dashboard's analytical data, not a production database.

## Recommendations

1. **Test a personal baseline goal:** Compare recent-baseline step targets with a fixed target among consenting users. Measure four-week active use, goal completion, and reminder opt-outs.
2. **Make sleep-data coverage visible:** Offer a weekly summary only with enough recorded nights; measure reporting completion, summary retention, and opt-outs.
3. **Test prompt timing:** Compare opt-in prompts near a user's usual active window with a fixed schedule. Monitor engagement and notification fatigue.
4. **Explain optional measurements:** Make consent and available coverage clear for weight and heart rate; track opt-in and repeat logging without health claims.

## Limitations

- The sample is small, observational, and from 2016. It contains no Bellabeat customer identity, demographics, sales, or campaign outcomes.
- Sleep, heart-rate, weight, and hourly records have different coverage. Missing values mean unknown; they cannot be safely treated as zero or ignored when discussing representativeness.
- Same-date activity and sleep do not establish event order or causality. Total recorded calories include baseline expenditure, not just exercise calories.
- The calculator reports **historical threshold attainment**, not a forecast. The default last-14-dates calculator window differs from the full-sample headline KPIs.
- Participant movement groups describe recorded step averages. They are not demographic or commercial customer segments.

## Project files

| File | Role |
| --- | --- |
| `app.py` | Streamlit dashboard, filters, charts, and scenario calculator |
| `sql_lab.py` | 30 questions, temporary SQLite tables, and read-only query runner |
| `Cleaned_Data/fitness_all_six_daily.csv` | Merged daily analytical data |
| `Cleaned_Data/hourly_activity.csv` | Hourly steps and calories |
| `client_storytelling.md` | Page-by-page client presentation script |
| `Bellabeat_Wellness_Project_Report.pdf` | Overall project report |

## Author
**Prepared by Ankan Chowdhury** 

Data Analysis, Dashboarding and SQL Practice case study.
