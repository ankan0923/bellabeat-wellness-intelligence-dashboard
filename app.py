from pathlib import Path
import base64
import html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sql_lab import QUESTIONS, make_connection, execute_readonly

st.set_page_config(page_title="Bellabeat Studio | Wellness intelligence", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
APP_DIR = Path(__file__).resolve().parent
ROOT = next((folder for folder in (APP_DIR / "Cleaned_Data", APP_DIR / "data", APP_DIR)
             if (folder / "fitness_all_six_daily.csv").is_file()), APP_DIR / "Cleaned_Data")
INK, MUTED, TEAL, LIME, CORAL, PURPLE = "#EAF7F5", "#A7BDC2", "#3AE0C8", "#D7F47A", "#FF948B", "#BEABFF"
PALETTE = [TEAL, CORAL, PURPLE, "#E4B65C", "#5C9FB8"]
IMAGE_DIR = APP_DIR / "images" if (APP_DIR / "images").is_dir() else APP_DIR

@st.cache_data(show_spinner=False)
def local_image(name):
    """Embed a provided image so it renders in HTML cards and hero backgrounds."""
    encoded = base64.b64encode((IMAGE_DIR / name).read_bytes()).decode("ascii")
    mime = "image/jpeg" if Path(name).suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64,{encoded}"

try:
    muscle_file = next((name for name in ("muscle_anatomy.png","muscle anatomy.png","anatomy.png")
                        if (IMAGE_DIR/name).is_file()), "muscle_anatomy.png")
    MUSCLE_IMAGE = local_image(muscle_file)
    RUN_IMAGE = local_image("movement.png")
    SLEEP_IMAGE = local_image("sleep.png")
except FileNotFoundError as exc:
    st.error(f"Missing image asset: {exc}. Place the PNGs beside app.py or inside an images folder.")
    st.stop()
SQL_IMAGE = local_image("sql.jpg") if (IMAGE_DIR / "sql.jpg").is_file() else None
HEART_IMAGE = local_image("H BIt.jpg") if (IMAGE_DIR / "H BIt.jpg").is_file() else None

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
:root{--ink:#eaf7f5;--muted:#a7bdc2;--teal:#3ae0c8;--line:#29424c}
html,body,[class*=css],.stApp{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:radial-gradient(circle at 88% 0%,#163c48 0%,#091923 43%,#07141d 100%)}
.block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:1480px}
[data-testid="stSidebar"]{background:#0a202b;border-right:1px solid #29424c}
[data-testid="stSidebar"] *{color:#eaf7f5!important}
[data-testid="stSidebar"] hr{border-color:#31505a}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:.27rem .2rem}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{font-size:.85rem}
[data-testid="stSidebar"] button{background:#164e57;color:#eaf7f5!important;border:1px solid #3b7075;border-radius:10px}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.045em;color:#eaf7f5}
h1{font-size:2.45rem!important;font-weight:800!important}h2{font-size:1.35rem!important;font-weight:800!important}
.hero{background:#123540;border:1px solid #34535c;border-radius:25px;padding:2rem 2.2rem;margin-bottom:1.4rem;position:relative;overflow:hidden;color:white;min-height:215px}
.hero.has-image{background-size:cover;background-position:center right}
.hero h1{color:white;margin:.3rem 0 .55rem;max-width:900px}.hero p{color:#d2e6e7;font-size:1rem;max-width:650px;margin:0}
.eyebrow{font-size:.78rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:#aef4d9}
.meta{font-size:.77rem;font-weight:700;letter-spacing:.07em;color:#a7bdc2;text-transform:uppercase;margin:.2rem 0 .55rem}
.kpi{background:#112934;border:1px solid #29424c;box-shadow:0 8px 26px #0003;border-radius:18px;padding:1rem 1.15rem;min-height:118px;margin-bottom:1rem}
.kpi .label{font-size:.79rem;color:#a7bdc2;font-weight:700}.kpi .value{font-family:Manrope,sans-serif;font-size:1.77rem;font-weight:800;letter-spacing:-.06em;color:#f2fbfa;margin:.25rem 0}
.kpi .detail{font-size:.73rem;color:#75e2d1;font-weight:700}.kpi.coral .detail{color:#ff948b}
.panel{background:#112934;border:1px solid #29424c;border-radius:18px;padding:1.2rem 1.25rem;margin:.35rem 0 1rem;box-shadow:0 8px 26px #0003}
.panel h3{font-size:1.12rem;margin:0 0 .5rem}.panel p{font-size:.9rem;color:#b9cdd0;line-height:1.55;margin:0}
.story-card{background:linear-gradient(145deg,#102b36,#10242e);border:1px solid #31505a;border-top:3px solid #3ae0c8;border-radius:16px;padding:1.1rem 1.25rem;margin:.4rem 0 1rem;min-height:200px}
.story-card .story-no{font-size:.75rem;letter-spacing:.14em;color:#76decf;font-weight:800}.story-card h3{margin:.4rem 0 .7rem;font-size:1.16rem}
.story-card p{font-size:.88rem;color:#c4d8da;line-height:1.55;margin:.3rem 0}.story-card b{color:#eaf7f5}
.callout{background:#12323a;border:1px solid #28515a;border-left:4px solid #3ae0c8;border-radius:12px;padding:.9rem 1.1rem;color:#cce7e5;margin:.5rem 0 1rem;font-size:.9rem}
.muscle-card{background:#102934;border:1px solid #29424c;border-radius:18px;padding:1rem;text-align:center;min-height:365px}
.muscle-card img{height:280px;max-width:100%;object-fit:contain;border-radius:8px;background:#fff}
.muscle-card small{display:block;color:#a7bdc2;margin-top:.55rem}
[data-testid="stTabs"] button p{font-weight:700;color:#c5d8d8}.stTabs [data-baseweb="tab-highlight"]{background:#3ae0c8}
[data-testid="stPlotlyChart"]{background:#102732;border:1px solid #29424c;border-radius:18px;box-shadow:0 8px 26px #0003;padding:.35rem}
[data-testid="stSlider"] [role="slider"]{background:#3ae0c8}
div.stButton>button[kind="primary"]{background:#1a8f87;border:1px solid #3ae0c8;color:white}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,textarea{background:#102934!important;color:#eaf7f5!important;border-color:#34535c!important}
[data-testid="stDataFrame"],code,pre{border-radius:12px}
a{color:#82e9d9!important}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load():
    d=pd.read_csv(ROOT/"fitness_all_six_daily.csv",parse_dates=["Date"])
    h=pd.read_csv(ROOT/"hourly_activity.csv",parse_dates=["Date","ActivityHour"])
    expected_daily={"Id","Date","TotalSteps","TotalActiveMinutes","SleepHours","SleepEfficiency",
                    "StepsGoalMet","ActivityLevel","DayName","DayType","Calories","WeightKg","BMI",
                    "HeartRateMean","HeartRateReadings","HourlyStepsTotal","HourlyCaloriesTotal"}
    expected_hourly={"Id","Date","ActivityHour","Hour","DayType","DayName","StepTotal","HourlyCalories","TimePeriod"}
    for name,frame,required in (("fitness_all_six_daily.csv",d,expected_daily),
                                ("hourly_activity.csv",h,expected_hourly)):
        missing=required-set(frame.columns)
        if missing:raise ValueError(f"{name} is missing columns: {', '.join(sorted(missing))}")
    d=d.drop_duplicates(["Id","Date"]).copy();h=h.drop_duplicates(["Id","ActivityHour"]).copy()
    for x in (d,h):
        x["Id"]=x.Id.astype(str)
        x["DayType"]=x.DayType.str.strip()
    return d,h
try:
    D,H=load()
except (FileNotFoundError,pd.errors.ParserError,ValueError) as exc:
    st.error(f"Data file could not be loaded: {exc}");st.stop()

st.sidebar.markdown("# ✦ Bellabeat")
st.sidebar.caption("WELLNESS INTELLIGENCE STUDIO")
st.sidebar.caption("DEGINED BY - ⍻⍿икαи")
st.sidebar.divider()
pages={"Project brief":"✦  Project brief","The pulse":"◉  The pulse","Movement":"↗  Movement","Sleep":"☾  Sleep","Daily rhythm":"◷  Daily Rhythm","Body signals":"♡  Body signals","Audience explorer":"◎  Audience Explorer","Goals & strategy":"◈  Goals & Strategy","Findings & actions":"▣  Findings & actions","SQL practice":"⌘  SQL Analysis"}
section=st.sidebar.radio("WORKSPACE",list(pages),format_func=lambda x:pages[x],label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.markdown("#### EXPLORE THE SAMPLE")
lo,hi=D.Date.min().date(),D.Date.max().date()
period=st.sidebar.date_input("Date range",(lo,hi),min_value=lo,max_value=hi)
if not isinstance(period,(list,tuple)) or len(period)!=2: st.info("Select both dates to continue.");st.stop()
start,end=period
all_ids=sorted(D.Id.unique())
people=st.sidebar.multiselect("Participants",all_ids,default=all_ids,help="Anonymous device IDs")
types=st.sidebar.multiselect("Day types",["Weekday","Weekend"],default=["Weekday","Weekend"])
if not people or not types or start>end: st.warning("Select at least one participant and day type, with a valid date range.");st.stop()
def filter_rows(frame):
    return frame[frame.Id.isin(people)&frame.Date.dt.date.between(start,end)&frame.DayType.isin(types)].copy()
d,h=filter_rows(D),filter_rows(H)
if d.empty: st.info("No records match these filters.");st.stop()
st.sidebar.divider()
st.sidebar.caption(f"{d.Id.nunique()} people · {len(d):,} days · {len(h):,} hours")
with st.sidebar.expander("Download filtered records"):
    st.download_button("Daily CSV",d.to_csv(index=False).encode(),"bellabeat_daily_filtered.csv","text/csv")
    st.download_button("Hourly CSV",h.to_csv(index=False).encode(),"bellabeat_hourly_filtered.csv","text/csv")
st.sidebar.caption("Fitbit sample · April–May 2016")
with st.sidebar.expander("Visual assets"):
    st.caption("Anatomy, movement, and sleep images supplied for this project. They are illustrative and do not represent measured participant anatomy or sleep physiology.")

def hero(tag,title,subtitle,image=None):
    style = f' style="background-image:linear-gradient(90deg,#0a202bf2 0%,#0a202bdc 47%,#0a202b55 100%),url(\'{image}\')"' if image else ""
    st.markdown(f'<div class="hero{" has-image" if image else ""}"{style}><div class="eyebrow">{tag}</div><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)
def card(label,value,detail="",accent=""):
    st.markdown(f'<div class="kpi {accent}"><div class="label">{html.escape(str(label))}</div><div class="value">{html.escape(str(value))}</div><div class="detail">{html.escape(str(detail))}</div></div>',unsafe_allow_html=True)
def insight(title,body):
    st.markdown(f'<div class="panel"><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></div>',unsafe_allow_html=True)
def action_card(number,title,evidence,test,measure):
    parts=(html.escape(str(value)) for value in (number,title,evidence,test,measure))
    number,title,evidence,test,measure=parts
    st.markdown(f'<div class="story-card"><div class="story-no">EXPERIMENT {number}</div><h3>{title}</h3>'
                f'<p><b>Evidence:</b> {evidence}</p><p><b>Test:</b> {test}</p>'
                f'<p><b>Measure:</b> {measure}</p></div>',unsafe_allow_html=True)
def callout(body): st.markdown(f'<div class="callout">{body}</div>',unsafe_allow_html=True)
def draw(fig,key):
    current_margin=fig.layout.margin
    margin=dict(l=current_margin.l if current_margin.l is not None else 35,
                r=current_margin.r if current_margin.r is not None else 35,
                t=current_margin.t if current_margin.t is not None else 65,
                b=current_margin.b if current_margin.b is not None else 45)
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color=INK,size=12),title_font=dict(family="Manrope",size=17,color=INK),margin=margin,height=fig.layout.height or 370,legend_title_text="",legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=MUTED)),hoverlabel=dict(bgcolor="#14343f",font_color=INK,bordercolor="#3d6870"))
    fig.update_xaxes(showgrid=False,linecolor="#35535d",title_font_color=MUTED)
    fig.update_yaxes(gridcolor="#29424c",zeroline=False,title_font_color=MUTED)
    st.plotly_chart(fig,use_container_width=True,key=key,config={"displaylogo":False,"scrollZoom":False})
def movement_donut_cluster(labels,counts,title,key):
    """Three independent small doughnuts compare participant movement groups."""
    items=[(str(label),int(value)) for label,value in zip(labels,counts)]
    total=sum(value for _,value in items)
    if not total:st.info("No participants are available for this chart.");return
    colors=["#D176B9","#B74DB8","#793CA4"]
    fig=go.Figure()
    for i,(label,value) in enumerate(items):
        share=100*value/total;color=colors[i%len(colors)]
        left=i/len(items)+.025;right=(i+1)/len(items)-.025
        fig.add_trace(go.Pie(values=[value,total-value],labels=[label,"Other groups"],hole=.73,
            sort=False,direction="clockwise",domain=dict(x=[left,right],y=[.19,.87]),
            marker=dict(colors=[color,"#29424c"],line=dict(color="#102732",width=2)),
            textinfo="none",showlegend=False,
            hovertemplate="%{label}<br>%{value} participants<extra></extra>"))
        # Plotly inscribes each pie in a square; the paper-domain midpoint can
        # drift away from the visible ring when three domains share a wide chart.
        center_x=(left+right)/2 + (i-(len(items)-1)/2)*.03
        fig.add_annotation(x=center_x,y=.53,text=f"<b>{share:.1f}%</b>",
                           showarrow=False,font=dict(size=21,color=INK))
        fig.add_annotation(x=center_x,y=.07,text=f"<b>{html.escape(label)}</b><br>{value} people",
                           showarrow=False,font=dict(size=13,color=color),align="center")
    fig.update_layout(height=350,showlegend=False,margin=dict(l=16,r=16,t=25,b=35))
    st.markdown(f"### {title}")
    st.caption(f"{total:,} eligible participants · each ring uses the same participant denominator")
    draw(fig,key)


def activity_multiring(labels,counts,title,key):
    """Distinct colored progress rings encode each activity band's share of days."""
    items=[(str(label),int(value)) for label,value in zip(labels,counts)]
    total=sum(value for _,value in items)
    if not total:st.info("No activity records are available.");return
    order={"Under 5k":0,"5k-7.5k":1,"7.5k-10k":2,"10k+":3}
    items.sort(key=lambda item:order.get(item[0],99))
    colors=["#FC887E","#E5B65B","#66C8D4","#3AE0C8"]
    fig=go.Figure()
    for i,(label,value) in enumerate(items):
        radius=.36+i*.15;share=100*value/total;color=colors[i%len(colors)]
        track=np.linspace(0,360,180)
        fig.add_trace(go.Scatterpolar(theta=track,r=np.full(len(track),radius),mode="lines",
            line=dict(color="#29424c",width=22),showlegend=False,hoverinfo="skip"))
        if value:
            arc=np.linspace(0,share*3.6,max(3,int(share*2)))
            fig.add_trace(go.Scatterpolar(theta=arc,r=np.full(len(arc),radius),mode="lines",
                line=dict(color=color,width=22),showlegend=False,
                hovertemplate=f"{html.escape(label)}: {value:,} days ({share:.1f}%)<extra></extra>"))
            fig.add_trace(go.Scatterpolar(theta=[arc[0],arc[-1]],r=[radius,radius],mode="markers",
                marker=dict(size=22,color=color),showlegend=False,hoverinfo="skip"))
        y=.83-i*.22
        fig.add_annotation(x=.64,y=y,text=f"<b>{html.escape(label)}</b><br>{value:,} participant-days",
                           xanchor="left",showarrow=False,font=dict(size=14,color=color),align="left")
        fig.add_annotation(x=.96,y=y,text=f"<b>{share:.1f}%</b>",xanchor="right",
                           showarrow=False,font=dict(size=17,color=color))
    fig.update_layout(polar=dict(domain=dict(x=[.01,.55],y=[.05,.95]),bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=False,range=[0,1.08]),angularaxis=dict(visible=False,direction="clockwise",rotation=90)),
        annotations=list(fig.layout.annotations)+[dict(x=.25,y=.5,text=f"<b>{total:,}</b><br>days",
            showarrow=False,font=dict(size=20,color=INK))],showlegend=False,height=410,
        margin=dict(l=20,r=20,t=20,b=20))
    st.markdown(f"### {title}")
    draw(fig,key)


def sleep_exploded_donut(labels,counts,key):
    """Exploded wedges show the share of observed nights in each duration band."""
    items=[(str(label),int(value)) for label,value in zip(labels,counts)]
    total=sum(value for _,value in items)
    if not total:st.info("No sleep records are available.");return
    colors=[CORAL,"#F7B746",TEAL,PURPLE]
    fig=go.Figure(go.Pie(labels=[label for label,_ in items],values=[value for _,value in items],
        hole=.56,pull=[.055,.025,.065,.04],sort=False,direction="clockwise",
        marker=dict(colors=colors,line=dict(color="#102732",width=3)),
        textinfo="percent",textposition="inside",insidetextfont=dict(size=15,color="white"),
        domain=dict(x=[.03,.61],y=[.07,.95]),
        hovertemplate="%{label}<br>%{value} recorded nights · %{percent}<extra></extra>",showlegend=True))
    fig.update_layout(height=400,legend=dict(x=.65,y=.83,orientation="v",font=dict(size=14)),
        annotations=[dict(x=.29,y=.5,text=f"<b>{total:,}</b><br>nights",showarrow=False,
                          font=dict(size=20,color=INK))],margin=dict(l=25,r=25,t=30,b=30))
    st.markdown("### Sleep duration composition")
    st.caption("Wedges represent recorded nights only; missing sleep stays out of the denominator.")
    draw(fig,key)

def mean(x):return f"{x:,.0f}" if pd.notna(x) else "—"
def rate(n,den):return n/den*100 if den else np.nan

if section=="Project brief":
    hero("CASE STUDY · WELLNESS BEHAVIOR","What can tracker records tell us?",
         "Explore movement, sleep reporting, and optional measurements to shape testable product ideas. The records are third-party Fitbit data, not Bellabeat customer behavior.",RUN_IMAGE)
    a,b,c,e=st.columns(4)
    with a:card("PARTICIPANTS",f"{d.Id.nunique():,}","anonymous device IDs")
    with b:card("RECORDED DAYS",f"{len(d):,}","participant-days")
    with c:card("HOURLY RECORDS",f"{len(h):,}","steps and calories")
    with e:card("SLEEP COVERAGE",f"{rate(d.SleepHours.notna().sum(),len(d)):.1f}%","of selected days")
    st.markdown("### The decision this project supports")
    insight("Business question","How do observed movement and sleep-recording patterns vary, and which wellness experiences should be tested first?")
    a,b,c=st.columns(3)
    with a:insight("01 · Prepare","Daily activity is one row per participant and date. Sleep and weight logs join by date; heart rate and hourly readings are summarized before the daily join.")
    with b:insight("02 · Explore","Compare activity bands, day and hour patterns, participant variation, sleep coverage, and optional body measurements using the same filters.")
    with c:insight("03 · Evaluate","Use the scenario calculator and SQL lab to inspect target attainment and validate the charts before proposing an experiment.")
    st.markdown("### Sources represented in this view")
    source_map=pd.DataFrame([
        ("Daily activity",f"{len(d):,} participant-days","Steps, distance, active time and total calories"),
        ("Sleep logs",f"{d.SleepHours.notna().sum():,} observed days","Duration and time in bed"),
        ("Hourly steps + calories",f"{len(h):,} participant-hours","Time-of-day movement and calories"),
        ("Weight logs",f"{d.WeightKg.notna().sum():,} observed days","Weight and recorded BMI"),
        ("Heart-rate readings",f"{d.HeartRateMean.notna().sum():,} summarized days","Count and daily range of available readings")],
        columns=["Source","Selected coverage","Used for"])
    st.dataframe(source_map,hide_index=True,use_container_width=True)
    callout("Scope: 12 April–12 May 2016. Missing sleep, weight and heart rate are unknown. Recorded calorie totals include baseline expenditure; the sample has no demographics, product purchases or Bellabeat customer IDs. Sidebar filters apply to every page.")

elif section=="The pulse":
    hero("01 · Executive snapshot","Your wellness story, at a glance","A focused view of movement, rest, and device usage across the selected participant-days.",RUN_IMAGE)
    cols=st.columns(5)
    vals=[("PEOPLE",str(d.Id.nunique()),f"{len(d):,} observed days"),("DAILY STEPS",mean(d.TotalSteps.mean()),"average per recorded day"),("ACTIVE TIME",f"{d.TotalActiveMinutes.mean():.0f} min","average per recorded day"),("STEP GOAL",f"{rate(d.StepsGoalMet.eq('Yes').sum(),len(d)):.0f}%","days with 10,000+ steps"),("SLEEP COVERAGE",f"{rate(d.SleepHours.notna().sum(),len(d)):.0f}%","days with sleep records")]
    for col,v in zip(cols,vals):
        with col:card(*v)
    trend=d.groupby("Date",as_index=False).agg(Steps=("TotalSteps","mean"),Low=("TotalSteps",lambda x:x.quantile(.25)),High=("TotalSteps",lambda x:x.quantile(.75)),Records=("Id","size"))
    trend["Rolling"]=trend.Steps.rolling(5,min_periods=1).mean()
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=trend.Date,y=trend.High,line=dict(width=0),showlegend=False,hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=trend.Date,y=trend.Low,fill="tonexty",fillcolor="rgba(58,224,200,.14)",line=dict(width=0),name="Middle 50% of days",hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=trend.Date,y=trend.Steps,mode="lines+markers",line=dict(color=TEAL,width=2),marker=dict(size=5),name="Daily mean",customdata=trend.Records,hovertemplate="%{x|%b %d}<br>%{y:,.0f} mean steps<br>%{customdata} records<extra></extra>"))
    fig.add_trace(go.Scatter(x=trend.Date,y=trend.Rolling,mode="lines",line=dict(color=LIME,width=3,shape="spline"),name="5-date rolling mean"))
    fig.add_hline(y=10000,line_dash="dash",line_color=CORAL,annotation_text="10k reference")
    fig.update_layout(title="Steps over time · variation and trend",yaxis_title="Steps per participant-day",xaxis_title="",hovermode="x unified")
    draw(fig,"pulse-trend")
    counts=d.ActivityLevel.value_counts()
    activity_multiring(counts.index,counts.values,"Activity mix · daily step bands","pulse-multiring")
    step_goal=rate(d.StepsGoalMet.eq("Yes").sum(),len(d))
    sleepers=d[d.SleepHours.notna()]
    a,b,c=st.columns(3)
    with a: insight("Movement opportunity",f"{100-step_goal:.0f}% of recorded days finished below 10,000 steps. Test flexible goals that adapt to each user's baseline.")
    with b: insight("Sleep visibility",f"Sleep is logged for {len(sleepers):,} of {len(d):,} days. A sleep-focused experience needs a clear opt-in and data-completion check.")
    with c: insight("Best next question","Use the Audience explorer to check participant variation before building a campaign around an overall average.")

elif section=="Movement":
    hero("02 · Movement intelligence","What drives an active day?","Inspect the weekly pattern, time allocation, and variation behind daily step totals.",RUN_IMAGE)
    a,b,c,e=st.columns(4)
    with a:card("AVG DISTANCE",f"{d.TotalDistance.mean():.1f} km","per participant-day")
    with b:card("VERY ACTIVE",f"{d.VeryActiveMinutes.mean():.0f} min","daily average")
    with c:card("SEDENTARY",f"{d.SedentaryMinutes.mean():.0f} min","daily average")
    with e:card("CALORIES",mean(d.Calories.mean()),"total daily calories")
    tab1,tab2,tab3=st.tabs(["Weekly pattern","Activity composition","Relationships"])
    order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    with tab1:
        byday=d.groupby("DayName",as_index=False).agg(Steps=("TotalSteps","mean"),Minutes=("TotalActiveMinutes","mean"),Count=("Id","size"))
        left,right=st.columns([1.4,1])
        with left:
            byday["DayName"]=pd.Categorical(byday.DayName,categories=order,ordered=True)
            byday=byday.sort_values("DayName")
            fig=go.Figure()
            for row in byday.itertuples():
                fig.add_shape(type="line",x0=row.DayName,x1=row.DayName,y0=0,y1=row.Steps,line=dict(color="#315863",width=8))
            fig.add_trace(go.Scatter(x=byday.DayName,y=byday.Steps,mode="markers+text",marker=dict(size=19,color=[TEAL if x>=8000 else CORAL for x in byday.Steps],line=dict(color="#0b202a",width=2)),text=byday.Steps.map(lambda x:f"{x:,.0f}"),textposition="top center",customdata=byday.Count,hovertemplate="%{x}<br>%{y:,.0f} mean steps<br>%{customdata} days<extra></extra>",showlegend=False))
            fig.add_hline(y=d.TotalSteps.mean(),line_dash="dot",line_color=LIME,annotation_text="Selected average")
            fig.update_layout(title="Weekly movement profile",yaxis_title="Mean daily steps")
            draw(fig,"move-week")
        with right:
            goal=d.groupby("DayType",as_index=False).agg(Reached=("StepsGoalMet",lambda x:x.eq("Yes").sum()),Total=("Id","size"))
            goal["Rate"]=goal.Reached/goal.Total*100
            fig=go.Figure()
            for i,row in enumerate(goal.itertuples()):
                domain=[0,1] if len(goal)==1 else ([0,.46] if i==0 else [.54,1])
                fig.add_trace(go.Indicator(
                    mode="gauge+number",value=row.Rate,
                    number=dict(suffix="%",font=dict(size=28,color=INK)),
                    title=dict(text=f"{row.DayType} · {row.Total} days",font=dict(size=13,color=MUTED)),
                    domain=dict(x=domain,y=[0,1]),
                    gauge=dict(axis=dict(range=[0,100],tickvals=[0,50,100],tickcolor=MUTED),
                               bar=dict(color=TEAL if row.DayType=="Weekday" else CORAL,thickness=.35),
                               bgcolor="#24414c",borderwidth=0)))
            fig.update_layout(title="10k goal completion",height=370)
            draw(fig,"move-goal")
    with tab2:
        fields={"VeryActiveMinutes":"Very active","FairlyActiveMinutes":"Fairly active","LightlyActiveMinutes":"Light activity","SedentaryMinutes":"Sedentary"}
        stack=d.groupby("DayType")[list(fields)].mean().reset_index().melt("DayType",var_name="Intensity",value_name="Minutes")
        stack.Intensity=stack.Intensity.map(fields)
        chart_col,anatomy_col=st.columns([1.6,.65])
        with chart_col:
            fig=px.bar(stack,x="Minutes",y="DayType",color="Intensity",orientation="h",barmode="stack",color_discrete_sequence=[TEAL,CORAL,PURPLE,"#54717a"],title="How a recorded day is spent",hover_data={"Minutes":":.0f"})
            fig.update_layout(legend=dict(orientation="h",y=-.28),height=365)
            fig.update_xaxes(title="Average recorded minutes");fig.update_yaxes(title="")
            draw(fig,"move-stack")
        with anatomy_col:
            st.markdown(f'<div class="muscle-card"><img src="{MUSCLE_IMAGE}" alt="User-provided human muscle illustration"><small>Human muscle anatomy · visual context only</small></div>',unsafe_allow_html=True)
        callout("Activity and sedentary minutes come from device records. Their sum may not equal a full day when wear time varies.")
    with tab3:
        left,right=st.columns(2)
        with left:
            fig=px.scatter(d,x="TotalSteps",y="Calories",color="DayType",size="TotalActiveMinutes",size_max=19,color_discrete_map={"Weekday":TEAL,"Weekend":CORAL},opacity=.55,hover_data=["Id","Date","TotalActiveMinutes"],title="Steps, calories, and active time")
            fig.add_vline(x=d.TotalSteps.median(),line_dash="dot",line_color="#8aa5ad",annotation_text="Median steps")
            fig.add_hline(y=d.Calories.median(),line_dash="dot",line_color="#8aa5ad",annotation_text="Median calories")
            draw(fig,"move-scatter")
        with right:
            fig=px.violin(d,x="ActivityLevel",y="TotalSteps",color="ActivityLevel",color_discrete_sequence=PALETTE,box=True,points=False,title="Step distribution by activity level")
            fig.update_layout(showlegend=False);draw(fig,"move-box")
        callout("Calories are total recorded calories, including baseline expenditure. These comparisons describe association rather than a causal effect of steps.")

elif section=="Sleep":
    hero("03 · Sleep intelligence","Rest, with the gaps visible","Sleep records are incomplete. Every sleep result below uses days with an observed sleep value.",SLEEP_IMAGE)
    s=d[d.SleepHours.notna()].copy()
    a,b,c,e=st.columns(4)
    with a:card("SLEEP RECORDS",f"{len(s):,} / {len(d):,}","observed participant-days")
    with b:card("AVG DURATION",f"{s.SleepHours.mean():.1f} h" if len(s) else "—","recorded nights")
    with c:card("EFFICIENCY",f"{s.SleepEfficiency.mean():.0f}%" if len(s) else "—","recorded nights")
    with e:card("7+ HOUR GOAL",f"{rate(s.SleepGoalMet.eq('Yes').sum(),len(s)):.0f}%" if len(s) else "—","of recorded sleep days")
    if s.empty: st.info("There are no sleep records in this selection.")
    else:
        fig=px.histogram(s,x="SleepHours",nbins=22,color_discrete_sequence=[PURPLE],opacity=.85,title="Sleep duration · observed nights")
        fig.add_vrect(x0=7,x1=9,fillcolor="rgba(58,224,200,.12)",line_width=0,annotation_text="7–9 h band")
        fig.add_vline(x=s.SleepHours.median(),line_dash="dash",line_color=LIME,annotation_text=f"Median {s.SleepHours.median():.1f} h")
        fig.update_yaxes(title="Recorded nights");draw(fig,"sleep-hist")
        bins=pd.cut(s.SleepHours,[0,6,7,9,float("inf")],labels=["Under 6h","6–7h","7–9h","9+h"],right=False)
        counts=bins.value_counts().reindex(["Under 6h","6–7h","7–9h","9+h"]).fillna(0)
        sleep_exploded_donut(counts.index,counts.values,"sleep-exploded")
        coverage_by_level=d.groupby("ActivityLevel",observed=True).agg(
            Days=("Id","size"),Recorded=("SleepHours","count")).reset_index()
        coverage_by_level["Coverage"]=100*coverage_by_level.Recorded/coverage_by_level.Days
        fig=go.Figure()
        fig.add_trace(go.Bar(y=coverage_by_level.ActivityLevel,x=[100]*len(coverage_by_level),
                             orientation="h",marker_color="#29424c",width=.6,hoverinfo="skip",showlegend=False))
        fig.add_trace(go.Bar(y=coverage_by_level.ActivityLevel,x=coverage_by_level.Coverage,
            orientation="h",marker_color=PURPLE,width=.6,text=coverage_by_level.Coverage.map(lambda x:f"{x:.1f}%"),
            textposition="outside",customdata=np.column_stack([coverage_by_level.Recorded,coverage_by_level.Days]),
            hovertemplate="%{y}<br>%{customdata[0]} of %{customdata[1]} days recorded sleep<br>%{x:.1f}% coverage<extra></extra>",showlegend=False))
        fig.update_layout(title="Sleep reporting by activity band · data coverage",barmode="overlay",height=330,
                          xaxis=dict(range=[0,112],ticksuffix="%",title="Days with sleep records"),yaxis_title="")
        draw(fig,"sleep-by-activity")
        st.caption("This compares recording coverage across step bands; it does not measure whether activity improves sleep.")
        left,right=st.columns(2)
        with left:
            fig=px.scatter(s,x="TotalSteps",y="SleepHours",color="DayType",size="SleepEfficiency",size_max=18,color_discrete_map={"Weekday":TEAL,"Weekend":CORAL},opacity=.62,hover_data=["Id","Date","SleepEfficiency"],title="Steps, sleep duration, and efficiency")
            fig.add_hrect(y0=7,y1=9,fillcolor="rgba(58,224,200,.08)",line_width=0)
            draw(fig,"sleep-relation")
        with right:
            coverage=d.groupby("Date",as_index=False).agg(Days=("Id","size"),Sleep=("SleepHours","count"))
            coverage["Share"]=100*coverage.Sleep/coverage.Days
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=coverage.Date,y=coverage.Share,mode="lines+markers",line=dict(color=PURPLE,width=3,shape="spline"),marker=dict(size=5),fill="tozeroy",fillcolor="rgba(190,171,255,.13)",customdata=np.column_stack([coverage.Sleep,coverage.Days]),hovertemplate="%{x|%b %d}<br>%{y:.0f}% coverage<br>%{customdata[0]} of %{customdata[1]} days<extra></extra>"))
            fig.update_layout(title="Sleep reporting through time",hovermode="x unified")
            fig.update_yaxes(range=[0,100],title="Days with sleep data (%)");draw(fig,"sleep-coverage")
    callout("Missing sleep is unknown rather than zero. Same-date steps and sleep do not establish whether sleep came before or after that day's movement.")

elif section=="Daily rhythm":
    hero("04 · Timing intelligence","Find the natural activity window","Hourly patterns can guide the timing of an opt-in movement prompt, subject to testing.")
    if h.empty: st.info("No hourly observations match this selection.")
    else:
        peak=int(h.groupby("Hour").StepTotal.mean().idxmax())
        a,b,c=st.columns(3)
        with a:card("PEAK HOUR",f"{peak:02d}:00","highest mean steps")
        with b:card("HOURLY STEPS",mean(h.StepTotal.mean()),"per observed hour")
        with c:card("OBSERVED HOURS",f"{len(h):,}","across selected participants")
        grouped=h.groupby(["Hour","DayType"],as_index=False).agg(Steps=("StepTotal","mean"),Records=("Id","size"))
        fig=px.line(grouped,x="Hour",y="Steps",color="DayType",markers=True,custom_data=["Records"],color_discrete_map={"Weekday":TEAL,"Weekend":CORAL},title="24-hour movement rhythm")
        fig.update_traces(line_width=3,marker_size=6,hovertemplate="%{x}:00 · %{y:,.0f} avg steps<br>%{customdata[0]} records<extra></extra>")
        fig.add_vrect(x0=max(0,peak-1),x1=min(23,peak+1),fillcolor="rgba(215,244,122,.1)",line_width=0,annotation_text="Peak window")
        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(dtick=2,title="Hour of day");fig.update_yaxes(title="Steps per observed hour")
        draw(fig,"rhythm-line")
        indexed=h.groupby("Hour",as_index=False).agg(Steps=("StepTotal","mean"),Calories=("HourlyCalories","mean"))
        for field in ("Steps","Calories"):
            baseline=indexed[field].mean()
            indexed[field+"Index"]=100*indexed[field]/baseline if baseline else np.nan
        fig=go.Figure()
        for field,color,label in (("StepsIndex",TEAL,"Steps"),("CaloriesIndex",CORAL,"Total hourly calories")):
            fig.add_trace(go.Scatter(x=indexed.Hour,y=indexed[field],mode="lines+markers",
                line=dict(color=color,width=3,shape="spline"),marker=dict(size=7),name=label,
                hovertemplate="%{x}:00 · %{y:.0f} index<extra>"+label+"</extra>"))
        fig.add_hline(y=100,line_dash="dot",line_color=MUTED,annotation_text="Each measure's own hourly mean")
        fig.update_layout(title="When steps and recorded calories rise above their own averages",height=350,
                          xaxis=dict(title="Hour of day",dtick=2),yaxis_title="Index · hourly mean = 100")
        draw(fig,"rhythm-index")
        st.caption("Each line is indexed separately so steps and total calories can be compared by timing, not by unit or causal effect.")
        left,right=st.columns([1.25,1])
        with left:
            week=h.groupby(["DayName","Hour"],as_index=False).StepTotal.mean()
            matrix=week.pivot(index="DayName",columns="Hour",values="StepTotal").reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
            fig=go.Figure(go.Heatmap(z=matrix.values,x=list(matrix.columns),y=list(matrix.index),colorscale=[[0,"#112934"],[.32,"#24515d"],[.7,"#38a6a8"],[1,LIME]],colorbar=dict(title="Steps",tickfont=dict(color=MUTED)),xgap=2,ygap=3,hovertemplate="%{y} %{x}:00<br>%{z:,.0f} avg steps<extra></extra>"))
            fig.update_layout(title="Activity clock by weekday",height=405,yaxis=dict(autorange="reversed"));draw(fig,"rhythm-heatmap")
        with right:
            periods=h.groupby("TimePeriod",as_index=False).agg(Steps=("StepTotal","mean"),Records=("Id","size"))
            periods=periods.sort_values("Steps")
            fig=go.Figure()
            fig.add_trace(go.Bar(x=periods.Steps,y=periods.TimePeriod,orientation="h",marker=dict(color=periods.Steps,colorscale=[[0,"#27525d"],[1,TEAL]],line=dict(width=0)),text=periods.Steps.map(lambda x:f"{x:,.0f}"),textposition="outside",customdata=periods.Records,hovertemplate="%{y}<br>%{x:,.0f} avg steps<br>%{customdata} recorded hours<extra></extra>"))
            fig.update_layout(title="Activity by time period",xaxis_title="Steps per observed hour",height=405);draw(fig,"rhythm-period")
        callout("The heatmap averages available hours. Hover to see counts on the line chart; differences in recording coverage can affect hourly comparisons.")

elif section=="Body signals":
    hero("05 · Optional measurements","Weight and heart-rate coverage","Explore the measurements available for selected participants, with missing records clearly shown.",HEART_IMAGE)
    weights=d[d.WeightKg.notna()].copy()
    hearts=d[d.HeartRateMean.notna()].copy()
    a,b,c,e=st.columns(4)
    with a:card("WEIGHT LOGS",f"{len(weights):,}",f"{weights.Id.nunique()} participants")
    with b:card("HEART-RATE DAYS",f"{len(hearts):,}",f"{hearts.Id.nunique()} participants")
    with c:card("RECORDED BMI",f"{d.BMI.notna().sum():,}","device-reported values")
    with e:card("HEART READINGS",f"{hearts.HeartRateReadings.sum():,.0f}","on observed heart-rate days")
    left,right=st.columns(2)
    with left:
        if hearts.empty:st.info("No heart-rate measurements match this selection.")
        else:
            person=st.selectbox("Heart-rate participant",sorted(hearts.Id.unique()),key="heart_person")
            observed=hearts[hearts.Id==person].sort_values("Date")
            fig=px.line(observed,x="Date",y="HeartRateMean",markers=True,
                        hover_data=["HeartRateReadings","HeartRateMin","HeartRateMax"],
                        title="Recorded daily mean heart rate")
            fig.update_traces(line_color=CORAL,marker_color=CORAL)
            fig.update_yaxes(title="Mean recorded heart rate (bpm)")
            draw(fig,"body-heart")
    with right:
        if weights.empty:st.info("No weight measurements match this selection.")
        else:
            person=st.selectbox("Weight participant",sorted(weights.Id.unique()),key="weight_person")
            observed=weights[weights.Id==person].sort_values("Date")
            fig=px.line(observed,x="Date",y="WeightKg",markers=True,hover_data=["BMI"],
                        title="Recorded weight logs")
            fig.update_traces(line_color=PURPLE,marker_color=PURPLE)
            fig.update_yaxes(title="Logged weight (kg)")
            draw(fig,"body-weight")
    callout("Weight and heart-rate tracking is sparse and comes from different participant subsets. A daily heart-rate mean summarizes available readings, not continuous monitoring. BMI is a recorded field, not a diagnosis.")

elif section=="Audience explorer":
    hero("06 · Segment discovery","Explore participant variation","Move from one overall average to observed behavior groups. Segments are descriptive, not demographic profiles.")
    summary=d.groupby("Id",as_index=False).agg(Days=("Date","size"),AvgSteps=("TotalSteps","mean"),StepSD=("TotalSteps","std"),AvgActive=("TotalActiveMinutes","mean"),GoalDays=("StepsGoalMet",lambda x:x.eq("Yes").sum()),SleepDays=("SleepHours","count"),AvgSleep=("SleepHours","mean"))
    summary["GoalRate"]=100*summary.GoalDays/summary.Days
    summary["SleepCoverage"]=100*summary.SleepDays/summary.Days
    summary["MovementGroup"]=pd.cut(summary.AvgSteps,[-1,5000,10000,float("inf")],labels=["Under 5k","5k–10k","10k+"])
    minimum=st.slider("Minimum recorded days per participant",1,max(1,int(summary.Days.max())),min(5,int(summary.Days.max())),help="Raise the threshold to reduce unstable participant averages.")
    eligible=summary[summary.Days>=minimum].copy()
    if eligible.empty: st.info("No participants meet that minimum. Lower the slider.")
    else:
        a,b,c=st.columns(3)
        with a:card("ELIGIBLE PEOPLE",str(len(eligible)),f"at least {minimum} observed days")
        with b:card("MEDIAN STEPS",mean(eligible.AvgSteps.median()),"median participant average")
        with c:card("STEP RANGE",f"{eligible.AvgSteps.min():,.0f}–{eligible.AvgSteps.max():,.0f}","participant averages")
        fig=px.scatter(eligible,x="AvgSteps",y="GoalRate",size="Days",size_max=30,color="MovementGroup",color_discrete_sequence=[CORAL,PURPLE,TEAL],hover_name="Id",hover_data=["Days","SleepCoverage"],title="Participant map · goals and movement")
        fig.add_vline(x=eligible.AvgSteps.median(),line_dash="dot",line_color="#91abb0",annotation_text="Median participant")
        fig.add_hline(y=eligible.GoalRate.median(),line_dash="dot",line_color="#91abb0")
        fig.update_xaxes(title="Average steps per recorded day");fig.update_yaxes(title="10k goal rate (%)",range=[0,105]);draw(fig,"audience-bubble")
        stable=eligible[eligible.Days>=2].copy()
        stable["StepCV"]=100*stable.StepSD/stable.AvgSteps.replace(0,np.nan)
        stable=stable.dropna(subset=["StepCV"])
        if not stable.empty:
            fig=px.scatter(stable,x="AvgSteps",y="StepCV",size="Days",size_max=27,color="GoalRate",
                color_continuous_scale=[[0,"#365669"],[.5,PURPLE],[1,TEAL]],hover_name="Id",
                hover_data={"Days":True,"GoalRate":":.1f","StepCV":":.1f"},
                title="Participant consistency · baseline versus daily variation")
            fig.update_xaxes(title="Mean steps per observed day")
            fig.update_yaxes(title="Step variation relative to mean (%)")
            draw(fig,"audience-consistency")
            st.caption("Lower variation means recorded step totals were more consistent. The comparison needs multiple days and excludes zero-mean participants.")
        grouped=eligible.MovementGroup.value_counts().reindex(["Under 5k","5k–10k","10k+"]).fillna(0)
        movement_donut_cluster(grouped.index,grouped.values,"Movement groups","audience-donuts")
        st.markdown("### Participant details")
        display=eligible[["Id","Days","AvgSteps","GoalRate","AvgActive","SleepCoverage","AvgSleep"]].rename(columns={"Id":"Device ID","Days":"Recorded days","AvgSteps":"Avg steps","GoalRate":"10k goal rate %","AvgActive":"Avg active min","SleepCoverage":"Sleep coverage %","AvgSleep":"Avg sleep h"}).round(1)
        st.dataframe(display,use_container_width=True,hide_index=True)
        st.download_button("Download participant summary",display.to_csv(index=False).encode(),"participant_summary.csv","text/csv")
    callout("Movement groups use participant mean steps and the chosen minimum observation count. The source has no age, gender, purchase, or Bellabeat customer status fields.")

elif section=="Goals & strategy":
    hero("07 · Scenario studio", "Goals & strategy", "Explore personal targets against actual device history, then turn the pattern into a testable Bellabeat idea.", RUN_IMAGE)
    options=["All selected participants"]+sorted(d.Id.unique())
    selected_person=st.selectbox("Analyze",options,help="Anonymous device IDs. All selected participants uses participant-days as observations.")
    history=d if selected_person==options[0] else d[d.Id==selected_person].copy()
    horizon=st.radio("Baseline window",["Last 7 dates","Last 14 dates","All filtered dates"],index=1,horizontal=True)
    if horizon!="All filtered dates":
        number=7 if horizon=="Last 7 dates" else 14
        dates_to_keep=sorted(history.Date.unique())[-number:]
        history=history[history.Date.isin(dates_to_keep)].copy()
    sleep_rows=history[history.SleepHours.notna()].copy()
    st.caption(f"{len(history):,} observed participant-days · {history.Date.nunique()} dates · {len(sleep_rows):,} days with sleep data")
    st.markdown("### Set your scenario")
    x,y,z=st.columns(3)
    with x:steps_target=st.slider("Daily step target",2000,20000,8000,500,key="lab_steps")
    with y:minutes_target=st.slider("Daily active-minute target",30,500,180,10,key="lab_minutes")
    with z:sleep_target=st.slider("Sleep target on recorded nights (h)",4.0,10.0,7.0,0.5,key="lab_sleep")
    avg_steps=history.TotalSteps.mean();avg_minutes=history.TotalActiveMinutes.mean()
    avg_sleep=sleep_rows.SleepHours.mean()
    attainment={
        "Steps":rate(history.TotalSteps.ge(steps_target).sum(),len(history)),
        "Active minutes":rate(history.TotalActiveMinutes.ge(minutes_target).sum(),len(history)),
        "Sleep":rate(sleep_rows.SleepHours.ge(sleep_target).sum(),len(sleep_rows)) if len(sleep_rows) else np.nan,
    }
    k1,k2,k3,k4=st.columns(4)
    with k1:card("BASELINE STEPS",mean(avg_steps),f"{max(0,steps_target-avg_steps):,.0f} to target per day")
    with k2:card("BASELINE ACTIVE TIME",f"{avg_minutes:.0f} min",f"{max(0,minutes_target-avg_minutes):,.0f} min to target")
    with k3:card("BASELINE SLEEP",f"{avg_sleep:.1f} h" if len(sleep_rows) else "—",f"{len(sleep_rows)} recorded sleep days")
    with k4:card("STEP TARGET MET",f"{attainment['Steps']:.0f}%",f"{len(history)} eligible days")
    scenario_tab,pattern_tab,marketing_tab=st.tabs(["Target simulator","History & consistency","Marketing experiments"])
    with scenario_tab:
        left,right=st.columns([1.25,1])
        with left:
            names=["Steps","Active minutes","Sleep"]
            values=[attainment[name] for name in names]
            fig=go.Figure()
            for i,(label,value,color) in enumerate(zip(names,values,[TEAL,CORAL,PURPLE])):
                fig.add_trace(go.Bar(x=[100],y=[label],orientation="h",marker=dict(color="#24414c"),showlegend=False,hoverinfo="skip",width=.55))
                if pd.notna(value):
                    fig.add_trace(go.Bar(x=[value],y=[label],orientation="h",marker=dict(color=color),text=[f"{value:.1f}%"],textposition="inside",textfont=dict(color="#07141d",size=14),showlegend=False,customdata=[len(sleep_rows) if label=="Sleep" else len(history)],hovertemplate="%{y}: %{x:.1f}%<br>%{customdata} records<extra></extra>",width=.55))
            fig.update_layout(title="Historical target attainment",barmode="overlay",xaxis=dict(range=[0,105],ticksuffix="%",title="Share of eligible records"),yaxis=dict(categoryorder="array",categoryarray=names[::-1]),height=340)
            draw(fig,"lab-bullet")
        with right:
            gap=max(0,steps_target-avg_steps)
            insight("Seven-day arithmetic",f"Maintaining the selected target for seven days would total {steps_target*7:,} steps. At the observed average, seven days would total about {avg_steps*7:,.0f}, a difference of {gap*7:,.0f}. This does not predict a change in behavior.")
            insight("Sleep denominator",f"The sleep target uses {len(sleep_rows):,} nights with observed sleep; missing nights are excluded from its rate.")
        steps_axis=np.arange(2000,20001,500)
        curve=np.array([rate(history.TotalSteps.ge(t).sum(),len(history)) for t in steps_axis])
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=steps_axis,y=curve,mode="lines",line=dict(color=TEAL,width=4,shape="spline"),fill="tozeroy",fillcolor="rgba(58,224,200,.10)",name="Historical share",hovertemplate="Target %{x:,.0f} steps<br>%{y:.1f}% of days<extra></extra>"))
        fig.add_trace(go.Scatter(x=[steps_target],y=[attainment["Steps"]],mode="markers+text",marker=dict(size=16,color=CORAL,line=dict(width=3,color="#102732")),text=[f"{attainment['Steps']:.0f}%"],textposition="top center",name="Your target",hovertemplate=f"{steps_target:,} steps<br>{attainment['Steps']:.1f}% of days<extra></extra>"))
        fig.update_layout(title="How target difficulty changes historical attainment",xaxis_title="Daily step threshold",yaxis_title="Participant-days reaching threshold (%)",yaxis_range=[0,105],height=340)
        draw(fig,"lab-threshold")
    with pattern_tab:
        left,right=st.columns([1.4,1])
        with left:
            series=history.groupby("Date",as_index=False).agg(Steps=("TotalSteps","mean"),Days=("Id","size"))
            series["Rolling"]=series.Steps.rolling(min(5,len(series)),min_periods=1).mean()
            fig=go.Figure()
            fig.add_trace(go.Bar(x=series.Date,y=series.Steps,marker_color=[TEAL if x>=steps_target else "#315461" for x in series.Steps],opacity=.7,name="Daily average",customdata=series.Days,hovertemplate="%{x|%b %d}: %{y:,.0f} steps<br>%{customdata} records<extra></extra>"))
            fig.add_trace(go.Scatter(x=series.Date,y=series.Rolling,mode="lines+markers",line=dict(color=CORAL,width=3),marker=dict(size=5),name="5-date rolling mean"))
            fig.add_hline(y=steps_target,line_dash="dash",line_color=LIME,annotation_text="Selected target")
            fig.update_layout(title="Observed steps with a rolling baseline",yaxis_title="Average steps",barmode="overlay",height=380)
            draw(fig,"lab-history")
        with right:
            both=history.TotalSteps.ge(steps_target)&history.TotalActiveMinutes.ge(minutes_target)
            insight("Combined movement days",f"{both.sum():,} of {len(history):,} observed days ({rate(both.sum(),len(history)):.1f}%) met both movement targets.")
            if selected_person!=options[0]:
                goal_dates=history.loc[history.TotalSteps.ge(steps_target),"Date"].sort_values().drop_duplicates()
                if len(goal_dates):
                    runs=goal_dates.diff().dt.days.ne(1).cumsum()
                    longest=int(goal_dates.groupby(runs).size().max())
                else:
                    longest=0
                insight("Longest recorded step streak",f"{longest} consecutive calendar day{'s' if longest!=1 else ''} reached {steps_target:,} steps in this baseline window. Missing dates break a streak.")
                peers=d.groupby("Id").agg(Days=("Date","size"),AverageSteps=("TotalSteps","mean"))
                peers=peers[peers.Days>=min(5,len(history))]
                peer_share=rate(peers.AverageSteps.le(avg_steps).sum(),len(peers)) if len(peers) else np.nan
                insight("Participant comparison",f"The selected person's baseline is at or above {peer_share:.0f}% of eligible participants' mean steps in the sidebar selection." if pd.notna(peer_share) else "Too few comparable participants for a ranking.")
            else:
                insight("Interpretation","The overall view weights each observed participant-day equally. Use an individual device ID to see a person's recent pattern.")
        callout("The baseline window selects observed dates, which may include multiple participants in the overall view. A rolling line smooths the recorded series; it is not a forecast.")
    with marketing_tab:
        reference_goal=rate(history.TotalSteps.ge(10000).sum(),len(history))
        sleep_coverage=rate(d.SleepHours.notna().sum(),len(d))
        peak=int(h.groupby("Hour").StepTotal.mean().idxmax()) if len(h) else None
        a,b,c=st.columns(3)
        with a:insight("01 · Adaptive movement goal",f"At {steps_target:,} steps, {attainment['Steps']:.1f}% of selected historical days reached the target. Compare personalized and fixed goals in an opt-in experiment. Primary metric: four-week active use; guardrail: reminder opt-outs.")
        with b:insight("02 · Sleep summary",f"Sleep was recorded on {sleep_coverage:.1f}% of filtered participant-days. Test whether a simple opt-in sleep summary improves reporting completion; track opt-outs.")
        timing_text=(f"Peak observed step activity is around {peak:02d}:00. " if peak is not None else "Hourly activity is unavailable for these filters. ")
        with c:insight("03 · Message timing",timing_text+"Test personalized versus fixed send times. Measure engagement and notification fatigue.")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=[reference_goal,attainment["Steps"]],y=["Historical attainment"]*2,mode="lines",line=dict(color="#6d8f97",width=9),showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[reference_goal],y=["Historical attainment"],mode="markers+text",marker=dict(size=24,color="#7996a1",line=dict(width=3,color="#102732")),text=[f"10k: {reference_goal:.1f}%"],textposition="top center",name="10k reference",hovertemplate="10,000 steps: %{x:.1f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=[attainment["Steps"]],y=["Historical attainment"],mode="markers+text",marker=dict(size=24,color=TEAL,line=dict(width=3,color="#102732")),text=[f"{steps_target:,}: {attainment['Steps']:.1f}%"],textposition="bottom center",name="Selected target",hovertemplate=f"{steps_target:,} steps: %{{x:.1f}}%<extra></extra>"))
        fig.update_layout(title="Same days · two target thresholds",xaxis_title="Participant-days reaching target (%)",xaxis_range=[0,105],height=280,showlegend=False)
        draw(fig,"lab-marketing")
        callout("Both target rates use the same calculator baseline window. The sample is third-party Fitbit data from 2016, not Bellabeat customers. Campaign effects require first-party research and testing.")
    callout("These are user-defined targets and historical comparisons. The dashboard cannot diagnose health or estimate exercise calories from total calories. Recorded BMI values are sparse and are not used in the calculator.")
elif section=="Findings & actions":
    hero("DECISION BRIEF · FROM PATTERN TO TEST","What should we try next?",
         "Each recommendation pairs an observed pattern with an experiment and a measure of success. Findings update with the sidebar filters.",SLEEP_IMAGE)
    sleep_days=int(d.SleepHours.notna().sum())
    weight_people=d.loc[d.WeightKg.notna(),"Id"].nunique()
    heart_people=d.loc[d.HeartRateMean.notna(),"Id"].nunique()
    low_days=int(d.TotalSteps.lt(5000).sum())
    high_days=int(d.TotalSteps.ge(10000).sum())
    eight_rate=rate(d.TotalSteps.ge(8000).sum(),len(d))
    ten_rate=rate(high_days,len(d))
    peak_hour=int(h.groupby("Hour").StepTotal.mean().idxmax()) if len(h) else None
    st.markdown("### What the selected records show")
    a,b=st.columns(2)
    with a:
        insight("Movement has two substantial tails",f"{low_days:,} of {len(d):,} days ({rate(low_days,len(d)):.1f}%) were below 5,000 steps; {high_days:,} ({ten_rate:.1f}%) reached 10,000. A single average hides both patterns.")
        insight("Sleep visibility is limited",f"Sleep was recorded on {sleep_days:,} of {len(d):,} days ({rate(sleep_days,len(d)):.1f}%). Average sleep describes recorded nights only.")
    with b:
        insight("Targets change historical attainment",f"{eight_rate:.1f}% of selected days reached 8,000 steps versus {ten_rate:.1f}% reaching 10,000. This is a threshold comparison, not a prediction of future behavior.")
        insight("Optional signals have smaller samples",f"Weight was logged by {weight_people:,} of {d.Id.nunique():,} selected participants and heart rate was observed for {heart_people:,}. Treat both as opt-in analysis, not full-sample trends.")
    st.markdown("### Recommended experiments")
    a,b=st.columns(2)
    with a:
        action_card("01","Goals grounded in a personal baseline",
                    f"The 8k and 10k thresholds cover {eight_rate:.1f}% and {ten_rate:.1f}% of selected days.",
                    "Randomize consenting users to a recent-baseline goal or a fixed step target.",
                    "Four-week active use, goal completion and reminder opt-outs.")
        action_card("03","Timing that respects activity rhythms",
                    f"The highest observed mean hourly steps occur near {peak_hour:02d}:00." if peak_hour is not None else "No hourly records match the selection.",
                    "Compare an opt-in prompt near a user's usual active window with a fixed send time.",
                    "Prompt engagement and notification opt-outs.")
    with b:
        action_card("02","A sleep summary with honest coverage",
                    f"Only {sleep_days:,} of {len(d):,} selected days contain sleep duration.",
                    "Show a weekly summary only when enough nights were recorded, with a visible data-completeness label.",
                    "Sleep-reporting completion and summary retention.")
        action_card("04","Optional measurement follow-through",
                    f"Weight and heart-rate logs cover {weight_people:,} and {heart_people:,} selected participants.",
                    "Test a clear opt-in explanation and a simple review of available records.",
                    "Opt-in rate, repeat logging and opt-outs; avoid health claims.")
    callout("Conclusion: the strongest opportunity is to personalize goals while making data coverage visible. These third-party Fitbit records from 2016 are a small observational sample; Bellabeat impact requires first-party research and controlled testing.")
else:
    hero("08 · SQL analysis studio","SQL Analysis & Insights","This module is designed to demonstrate query design, aggregation, segmentation, KPI extraction and business storytelling — not just display SQL syntax.",SQL_IMAGE)
    a,b,c=st.columns(3)
    with a:card("CHALLENGES","30","15 intermediate · 15 advanced")
    with b:card("DAILY ROWS",f"{len(d):,}","table: fitness_all_six_daily")
    with c:card("HOURLY ROWS",f"{len(h):,}","table: hourly_activity")
    callout("SQLite syntax · Read-only SELECT queries · Up to 500 result rows shown · Dashboard filters apply to both SQL tables. The daily table contains aggregated heart-rate and hourly metrics. Query results refresh when you press Run query.")
    with st.expander("Explore table columns and data types"):
        table_name=st.selectbox("Table",["fitness_all_six_daily","hourly_activity"])
        sample=d if table_name=="fitness_all_six_daily" else h
        st.dataframe(pd.DataFrame({"Column":sample.columns,"Pandas type":sample.dtypes.astype(str).values}),hide_index=True,use_container_width=True)
        st.caption("Dates are stored as ISO strings (YYYY-MM-DD); ActivityHour includes a time. NULL represents missing CSV values.")
        st.dataframe(sample.head(3),hide_index=True,use_container_width=True)
    left,right=st.columns([1,1])
    with left:level=st.selectbox("Difficulty",["All","Intermediate","Advanced"])
    with right:category=st.selectbox("Topic",["All"]+sorted({item["category"] for item in QUESTIONS}))
    choices=[i for i,item in enumerate(QUESTIONS) if (level=="All" or item["level"]==level) and (category=="All" or item["category"]==category)]
    if not choices:st.info("No challenges match this combination.")
    else:
        selected_no=st.selectbox("Choose a challenge",choices,format_func=lambda i:f"{i+1:02d} · {QUESTIONS[i]['question']}")
        task=QUESTIONS[selected_no]
        st.markdown(f"### Question {selected_no+1:02d} · {task['level']}")
        st.write(task["question"])
        st.caption(f"Topic: {task['category']}")
        with st.expander("Show a hint"):st.write(task["hint"])
        editor_key=f"sql_editor_{selected_no}"
        if editor_key not in st.session_state:
            st.session_state[editor_key]="SELECT\n    -- Write your query here\nFROM fitness_all_six_daily\nLIMIT 10;"
        sql=st.text_area("SQL editor",key=editor_key,height=220,help="SQLite SELECT queries only. The selected filters determine the available rows.")
        run_col,solution_col=st.columns([1,3])
        with run_col:run=st.button("▶ Run query",type="primary",use_container_width=True)
        with solution_col:show_solution=st.toggle("Show reference solution",key=f"sql_solution_{selected_no}")
        if run:
            connection=None
            try:
                connection=make_connection(d,h)
                result,limited=execute_readonly(connection,sql)
                st.session_state["sql_last"]=(selected_no,result,limited)
            except Exception as exc:
                st.session_state.pop("sql_last",None)
                st.error(f"Query error: {exc}")
            finally:
                if connection is not None:connection.close()
        previous=st.session_state.get("sql_last")
        if previous is not None and previous[0]==selected_no:
            result,limited=previous[1:]
            st.success(f"Query completed · {len(result):,} rows displayed"+(" · More rows exist" if limited else ""))
            st.dataframe(result,hide_index=True,use_container_width=True)
            st.download_button("Download query result",result.to_csv(index=False).encode(),f"sql_question_{selected_no+1:02d}_result.csv","text/csv")
        if show_solution:
            st.markdown("#### Reference query")
            st.code(task["solution"],language="sql")
            st.caption("The reference query is one valid approach. Compare its logic and result with your own query.")
    callout("Participant IDs represent anonymous devices. The data does not contain Bellabeat customer identities, sales, marketing attribution, or demographic fields.")

st.divider()
st.caption(f"Bellabeat case study · {len(d):,} participant-days and {len(h):,} participant-hours selected · Source: fitness_all_six_daily and hourly_activity CSVs · April–May 2016")
