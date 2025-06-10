import streamlit as st
import psutil
import time
import plotly.graph_objs as go


st.set_page_config(layout="wide")
st.title("🖥️ Real-Time CPU Performance Monitor (1-Min Refresh)")

st.markdown("Tracks CPU usage per core every 1 minute. Useful for observing long-term behavior under low/high load.")

# System Info
cpu_count = psutil.cpu_count(logical=True)
cpu_freq = psutil.cpu_freq()
cpu_name = platform.processor()

st.sidebar.subheader("🧠 System Info")
st.sidebar.write(f"Logical CPUs: {cpu_count}")
st.sidebar.write(f"Base Frequency: {cpu_freq.min:.2f} MHz")
st.sidebar.write(f"Max Frequency: {cpu_freq.max:.2f} MHz")
st.sidebar.write(f"Processor: {cpu_name}")

if "AMD" in cpu_name.upper():
    st.sidebar.success("✅ AMD Processor Detected!")

refresh_rate = 60  # <- Set to 60 seconds (1 minute)

# For plotting
cpu_usages = [[] for _ in range(cpu_count)]
timestamps = []
plot_placeholders = [st.empty() for _ in range(cpu_count)]

# Live Loop
while True:
    timestamp = time.strftime("%H:%M:%S")
    timestamps.append(timestamp)

    cpu_percentages = psutil.cpu_percent(percpu=True)

    for i in range(cpu_count):
        cpu_usages[i].append(cpu_percentages[i])
        if len(cpu_usages[i]) > 60:  # Keep only last 60 minutes
            cpu_usages[i].pop(0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=cpu_usages[i],
            x=timestamps[-60:],
            mode='lines+markers',
            name=f'Core {i}',
            line=dict(shape='spline')
        ))
        fig.update_layout(
            title=f"Core {i} Usage",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            yaxis=dict(range=[0, 100])
        )
        plot_placeholders[i].plotly_chart(fig, use_container_width=True)

    time.sleep(refresh_rate)
