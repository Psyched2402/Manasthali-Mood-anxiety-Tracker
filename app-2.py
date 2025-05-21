
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# App title
st.title("🧠 Mood & Anxiety Tracker")

# Simulate a user login/profile section
st.sidebar.header("👤 User Profile")
user_name = st.sidebar.text_input("Your Name", value="Test User")
user_email = st.sidebar.text_input("Your Email", value="test@example.com")

# Load existing data or create new
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv", parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Name", "Email", "Mood Score", "Mood Label", "Anxiety Score", "Anxiety Frequency", "Triggers", "Notes"])

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
    st.markdown(f"**Selected Mood:** {mood_label}")

    anxiety_score = st.slider("Anxiety Intensity", min_value=0, max_value=5, value=0)
    anxiety_freq = st.selectbox("Anxiety Frequency", ["None", "Sometimes", "Half the time", "> half the time", "All the time", "Episodes/day"])

    triggers = st.multiselect("Triggers", ["T1", "T2", "T3", "T4"])
    notes = st.text_area("Optional Notes")

    submitted = st.form_submit_button("Submit Entry")
    if submitted:
        new_entry = pd.DataFrame([{
            "Date": date,
            "Name": user_name,
            "Email": user_email,
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
        st.experimental_rerun()

# Mood & Anxiety Graphs
if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"]).dt.date
    user_data = data[data["Email"] == user_email]

    if not user_data.empty:
        st.subheader("📈 Mood & Anxiety Trends")

        last_30_days = user_data[user_data["Date"] >= datetime.date.today() - datetime.timedelta(days=30)]

        if not last_30_days.empty:
            mood_fig = px.line(last_30_days, x="Date", y="Mood Score", title="Mood Trend", markers=True)
            st.plotly_chart(mood_fig)

            anxiety_fig = px.line(last_30_days, x="Date", y="Anxiety Score", title="Anxiety Trend", markers=True)
            st.plotly_chart(anxiety_fig)

            st.subheader("🧠 Your Logged Entries")
            st.dataframe(last_30_days.sort_values("Date", ascending=False))
        else:
            st.info("No entries in the last 30 days.")
    else:
        st.info("No data found for this user.")
else:
    st.info("No data logged yet. Add your first entry above.")
