
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# App title
st.title("🧠 Mood & Anxiety Tracker")

# Load existing data or create new
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv", parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Mood Score", "Mood Label", "Anxiety Score", "Anxiety Frequency", "Triggers", "Notes"])

data = load_data()

# Input form
st.subheader("📅 Log Today’s Mood & Anxiety")
with st.form("log_form"):
    today = datetime.date.today()
    date = st.date_input("Date", value=today)

    mood_score = st.slider("Mood Intensity", min_value=-5, max_value=5, value=0)
    mood_labels = {
        5: "Euphoric", 4: "Excited", 3: "Very Good", 2: "Good", 1: "Fair", 0: "Neutral",
        -1: "Not good", -2: "Sad", -3: "Very sad", -4: "Melancholic", -5: "Suicidal"
    }
    mood_label = mood_labels[mood_score]

    anxiety_score = st.slider("Anxiety Intensity", min_value=0, max_value=5, value=0)
    anxiety_freq = st.selectbox("Anxiety Frequency", ["None", "Sometimes", "Half the time", "> half the time", "All the time", "Episodes/day"])

    triggers = st.multiselect("Triggers", ["T1", "T2", "T3", "T4"])
    notes = st.text_area("Optional Notes")

    submitted = st.form_submit_button("Submit Entry")
    if submitted:
        new_entry = pd.DataFrame([{
            "Date": date,
            "Mood Score": mood_score,
            "Mood Label": mood_label,
            "Anxiety Score": anxiety_score,
            "Anxiety Frequency": anxiety_freq,
            "Triggers": ", ".join(triggers),
            "Notes": notes
        }])
        data = pd.concat([data, new_entry], ignore_index=True)
        data.to_csv("data.csv", index=False)
        st.success("Entry saved!")

# Mood trend graph
if not data.empty:
    st.subheader("📈 Mood & Anxiety Trends")
    monthly = data[data["Date"] >= pd.to_datetime(datetime.date.today() - datetime.timedelta(days=30))]

    mood_fig = px.line(monthly, x="Date", y="Mood Score", title="Mood Trend", markers=True)
    st.plotly_chart(mood_fig)

    anxiety_fig = px.line(monthly, x="Date", y="Anxiety Score", title="Anxiety Trend", markers=True)
    st.plotly_chart(anxiety_fig)

    st.subheader("🧠 Logged Entries")
    st.dataframe(monthly.sort_values("Date", ascending=False))
else:
    st.info("No data logged yet. Add your first entry above.")
