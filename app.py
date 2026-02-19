import streamlit as st
import pandas as pd
import plotly.express as px
import time
import re
from collections import Counter

# Importing your friend's logic files
from youtube_api import (
    get_video_ids,
    fetch_video_stats,
    get_channel_country
)
from sentiment import analyze_sentiment
from summary import generate_summary

# NEW: Technical Guruji signature tech & unboxing hashtags
STATIC_TECH_TRENDS_TG = {
    "#technicalguruji": 2500,
    "#tgfamily": 2100,
    "#unboxing": 1800,
    "#smartphone": 1650,
    "#gadgets": 1400,
    "#technews": 1250,
    "#iphone17": 1100,
    "#samsung": 950,
    "#techshorts": 800,
    "#india": 750
}

static_df = pd.DataFrame(
    STATIC_TECH_TRENDS_TG.items(),
    columns=["Hashtag", "Frequency"]
)

# Page Configuration
st.set_page_config(page_title="TG Tech Intelligence", layout="wide")
st.title("🌟 Technical Guruji: Audience & Content Insights")
st.markdown("Real-time analysis of the world's largest Hindi tech channel.")

# Sidebar
# Default: Technical Guruji Official Channel ID
CHANNEL_ID = st.sidebar.text_input(
    "Channel ID to Track",
    "UCOhHO2ICt0ti9KAh-QHvttQ" 
)
refresh = st.sidebar.slider("Scan Frequency (seconds)", 30, 300, 60)

@st.cache_data(ttl=refresh)
def load_data():
    video_ids = get_video_ids(CHANNEL_ID)
    df = pd.DataFrame(fetch_video_stats(video_ids))
    df["published_at"] = pd.to_datetime(df["published_at"])
    return df

df = load_data()

if df.empty:
    st.error("Target channel data not found. Check the ID.")
    st.stop()

# Data Transformation
df["sentiment"], df["sentiment_score"] = zip(*df["title"].apply(analyze_sentiment))
df["engagement_total"] = df["likes"] + df["comments"]

summary = generate_summary(df)
country = get_channel_country(CHANNEL_ID)

# Metric Scorecard
st.subheader("📊 Channel Scorecard")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Uploads", summary["Total Videos"])
kpi2.metric("Total Views", f"{summary['Total Views']:,}")
kpi3.metric("Avg Video Engagement", f"{summary['Average Engagement']:.0f}")
kpi4.metric("Market Region", country)

st.divider()

# Trend Analysis
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.plotly_chart(
        px.line(
            df.sort_values("published_at"),
            x="published_at",
            y="views",
            title="📈 Viewership Trend (Last 50 Videos)",
            color_discrete_sequence=['#FFD700'] # Gold color
        ),
        use_container_width=True
    )

with chart_col2:
    st.plotly_chart(
        px.bar(
            df.sort_values("engagement_total", ascending=False).head(10),
            x="title",
            y="engagement_total",
            title="🏆 Highest Engagement Titles",
            color="engagement_total",
            color_continuous_scale="Greys"
        ),
        use_container_width=True
    )

st.divider()

# Sentiment Distribution
st.plotly_chart(
    px.histogram(
        df,
        x="sentiment",
        color="sentiment",
        title="💬 Audience Title Sentiment (Pos vs Neg)",
        category_orders={"sentiment": ["Positive", "Neutral", "Negative"]},
        color_discrete_map={'Positive':'#2ecc71', 'Neutral':'#bdc3c7', 'Negative':'#e74c3c'}
    ),
    use_container_width=True
)

# Hashtag Counter
def find_hashtags(text):
    return re.findall(r"#\w+", text.lower())

all_tags = []
for entry in df["title"]:
    all_tags.extend(find_hashtags(entry))

tag_data = Counter(all_tags).most_common(10)
live_hashtag_df = pd.DataFrame(tag_data, columns=["Hashtag", "Frequency"])

# Display Hashtags
display_df = live_hashtag_df if not live_hashtag_df.empty else static_df
st.plotly_chart(
    px.bar(
        display_df,
        x="Hashtag",
        y="Frequency",
        title="🔥 Trending Topics in Hindi Tech",
        color="Frequency",
        color_continuous_scale="YlOrBr"
    ),
    use_container_width=True
)

st.divider()
st.subheader("📄 Raw Video Data Feed")
st.dataframe(df.sort_values("published_at", ascending=False), use_container_width=True)

# Loop refresh logic
time.sleep(refresh)
st.rerun()