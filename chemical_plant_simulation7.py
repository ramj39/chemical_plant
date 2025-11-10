import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
# Sidebar sliders for background color
st.sidebar.header("Background Color Controls")
r = st.sidebar.slider("Red", 0, 255, 240)
g = st.sidebar.slider("Green", 0, 255, 242)
b = st.sidebar.slider("Blue", 0, 255, 246)
bg_color = f"rgb({r}, {g}, {b})"

# Inject custom CSS for background color
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        min-height: 100vh;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

#streamlit run chemical_plant_simulation6.py
st.title("🧪 Chemical Process Movement Designer")

# Sidebar inputs
st.sidebar.header("🔧 Input Variables")
num_stations = st.sidebar.number_input("Number of Stations", min_value=1, max_value=50, value=20)
num_transporters = st.sidebar.number_input("Number of Transporters", min_value=1, max_value=10, value=3)
cycle_time_min = st.sidebar.number_input("Cycle Time per Unit (minutes)", min_value=1.0, max_value=60.0, value=6.0)
units_per_hour = st.sidebar.number_input("Target Output (units/hour)", min_value=1, max_value=100, value=10)

# Station-specific durations
st.sidebar.subheader("⏱️ Station Durations (seconds)")
default_durations = {
    1: 300, 2: 120, 3: 30, 4: 30, 5: 30, 6: 30, 7: 30, 8: 120, 9: 45,
    10: 600, 11: 600, 12: 600, 13: 30, 14: 30, 15: 30, 16: 120, 17: 300, 18: 300
}
station_durations = {}
for i in range(1, num_stations + 1):
    station_durations[i] = st.sidebar.number_input(f"Station {i} Time", min_value=1, max_value=600,
                                                   value=default_durations.get(i, 30))

# Transporter coverage logic
stations_per_transporter = num_stations // num_transporters
transporters = {}
for i in range(num_transporters):
    start = i * stations_per_transporter + 1
    end = (i + 1) * stations_per_transporter if i < num_transporters - 1 else num_stations
    transporters[f"t{i+1}"] = list(range(start, end + 1))

# Generate movement schedule
unit_starts = [i * cycle_time_min for i in range(units_per_hour)]
records = []
for unit_id, offset in enumerate(unit_starts):
    unit_start = datetime(2025, 10, 20, 9, 0) + timedelta(minutes=offset)
    for t_name, stations in transporters.items():
        time_cursor = unit_start
        for station in stations:
            duration = station_durations.get(station, 30)
            records.append({
                "trans": t_name,
                "stn": station,
                "time": int((time_cursor - datetime(2025, 10, 20, 9, 0)).total_seconds())
            })
            time_cursor += timedelta(seconds=duration)

df = pd.DataFrame(records)

# Line graph
fig, ax = plt.subplots(figsize=(12, 6))
for trans in df['trans'].unique():
    subset = df[df['trans'] == trans]
    ax.plot(subset['time'], subset['stn'], marker='o', label=trans)

ax.set_title("📈 Transporter Movement Over Time")
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Station")
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)
st.pyplot(fig)

# CSV export
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Movement Data as CSV", data=csv, file_name="movement_schedule.csv", mime="text/csv")

# Graph export
buf_png = io.BytesIO()
fig.savefig(buf_png, format="png")
buf_png.seek(0)
st.download_button("🖼️ Download Graph as PNG", data=buf_png, file_name="movement_graph.png", mime="image/png")
