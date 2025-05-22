
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# ----------------------------
# CONFIGURATION
# ----------------------------
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "Mood_Anxiety_Tracker"
SPREADSHEET_ID = st.secrets["private_gsheets"]["sheet_id"]

# ----------------------------
# CONNECT TO GOOGLE SHEETS
# ----------------------------
credentials = Credentials.from_service_account_info(
    st.secrets["private_gsheets"],
    scopes=SCOPE
)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.worksheet(SHEET_NAME)

# ----------------------------
# APP UI
# ----------------------------
st.title("🧠 Mood & Anxiety Tracker")

# Simulated user profile
st.sidebar.header("👤 User Profile")
user_name = st.sidebar.text_input("Your Name", value="Test User")
user_email = st.sidebar.text_input("Your Email", value="test@example.com")

# Mood labels and scores
mood_labels = {
    5: "Euphoric", 4: "Excited", 3: "Very Good", 2: "Good", 1: "Fair", 0: "Neutral",
    -1: "Not good", -2: "Sad", -3: "Very sad", -4: "Melancholic", -5: "Suicidal"
}
label_to_score = {v: k for k, v in mood_labels.items()}

# ----------------------------
# FORM INPUT
# ----------------------------
st.subheader("📅 Log Today’s Mood & Anxiety")
with st.form("log_form"):
    today = datetime.date.today()
    date = st.date_input("Date", value=today)

    mood_label = st.radio("Select Your Mood", list(label_to_score.keys()))
    mood_score = label_to_score[mood_label]

    anxiety_score = st.slider("Anxiety Intensity", min_value=0, max_value=5, value=0)
    anxiety_freq = st.selectbox("Anxiety Frequency", ["None", "Sometimes", "Half the time", "> half the time", "All the time", "Episodes/day"])

    triggers = st.multiselect("Triggers", ["T1", "T2", "T3", "T4"])
    notes = st.text_area("Optional Notes")

    submitted = st.form_submit_button("Submit Entry")
    if submitted:
        new_row = [str(date), user_name, user_email, mood_score, mood_label, anxiety_score, anxiety_freq, ", ".join(triggers), notes]
        worksheet.append_row(new_row)
        st.success("Entry saved!")
        st.stop()

# ----------------------------
# LOAD DATA
# ----------------------------
data = pd.DataFrame(worksheet.get_all_records())
data["Date"] = pd.to_datetime(data["Date"]).dt.date
user_data = data[data["Email"] == user_email]

# ----------------------------
# DISPLAY CHARTS
# ----------------------------
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
    st.info("No data logged yet. Add your first entry above.")
