# app.py
import streamlit as st
import psutil
import time
import plotly.graph_objects as go
from collections import deque
import os

# Initialize session state
if 'cpu_data' not in st.session_state:
    st.session_state.cpu_data = deque(maxlen=60)
    st.session_state.mem_data = deque(maxlen=60)
    st.session_state.per_core_data = {}
    st.session_state.running = True

# Set up page
st.set_page_config(
    page_title="Real-Time CPU Monitor",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for AMD-inspired styling
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
    
    :root {{
        --amd-red: #ED1C24;
        --amd-dark: #000000;
        --amd-gray: #2D2D2D;
    }}
    
    body {{
        background-color: var(--amd-dark);
        color: white;
        font-family: 'Roboto Mono', monospace;
    }}
    
    .metric-box {{
        background: var(--amd-gray);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid var(--amd-red);
    }}
    
    .stButton>button {{
        background: var(--amd-red) !important;
        color: white !important;
        border: none;
        font-weight: bold;
    }}
    
    .header {{
        border-bottom: 2px solid var(--amd-red);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    
    .plot-container {{
        background: var(--amd-gray);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='header'><h1>🚀 AMD-Style CPU Performance Monitor</h1></div>", unsafe_allow_html=True)

# Initialize per-core data if needed
if not st.session_state.per_core_data:
    for i in range(psutil.cpu_count()):
        st.session_state.per_core_data[i] = deque(maxlen=60)

# Control panel
st.sidebar.markdown("## 🛠️ Control Panel")
if st.sidebar.button('⏸️ Pause Monitoring'):
    st.session_state.running = False
if st.sidebar.button('▶️ Resume Monitoring'):
    st.session_state.running = True

st.sidebar.markdown("### System Info")
st.sidebar.text(f"OS: {os.name.upper()}")
st.sidebar.text(f"CPU Cores: {psutil.cpu_count()}")
st.sidebar.text(f"CPU Freq: {psutil.cpu_freq().current:.0f} MHz")
st.sidebar.text(f"Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")

# Main dashboard
placeholder = st.empty()

while True:
    if st.session_state.running:
        # Get system metrics
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent
        per_cpu = psutil.cpu_percent(percpu=True)
        
        # Update data
        st.session_state.cpu_data.append(cpu_percent)
        st.session_state.mem_data.append(mem_percent)
        
        for i, percent in enumerate(per_cpu):
            st.session_state.per_core_data[i].append(percent)
        
        # Build the dashboard
        with placeholder.container():
            # Real-time metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"<div class='metric-box'><h3>Total CPU</h3><h1>{cpu_percent}%</h1></div>", 
                            unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div class='metric-box'><h3>Memory</h3><h1>{mem_percent}%</h1></div>", 
                            unsafe_allow_html=True)
            
            with col3:
                load = ", ".join([f"{p}%" for p in per_cpu])
                st.markdown(f"<div class='metric-box'><h3>Per Core Load</h3><p>{load}</p></div>", 
                            unsafe_allow_html=True)
            
            # CPU Usage Plot
            st.markdown("<div class='plot-container'><h3>📈 CPU Usage History (Last 60s)</h3></div>", 
                        unsafe_allow_html=True)
            fig_cpu = go.Figure()
            fig_cpu.add_trace(go.Scatter(
                x=list(range(len(st.session_state.cpu_data))),
                y=list(st.session_state.cpu_data),
                name="Total CPU",
                line=dict(color='#ED1C24', width=3)
            )
            fig_cpu.update_layout(
                yaxis=dict(range=[0, 100], title="Percentage"),
                xaxis=dict(title="Seconds Ago"),
                height=300,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_cpu, use_container_width=True)
            
            # Per-core CPU Usage
            st.markdown("<div class='plot-container'><h3>🔥 Per-Core CPU Usage</h3></div>", 
                        unsafe_allow_html=True)
            fig_cores = go.Figure()
            for i, data in st.session_state.per_core_data.items():
                fig_cores.add_trace(go.Scatter(
                    x=list(range(len(data))),
                    y=list(data),
                    name=f"Core {i+1}",
                    line=dict(width=2)
                ))
            fig_cores.update_layout(
                yaxis=dict(range=[0, 100], title="Percentage"),
                xaxis=dict(title="Seconds Ago"),
                height=300,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_cores, use_container_width=True)
            
            # Memory Usage Plot
            st.markdown("<div class='plot-container'><h3>💾 Memory Usage History (Last 60s)</h3></div>", 
                        unsafe_allow_html=True)
            fig_mem = go.Figure()
            fig_mem.add_trace(go.Scatter(
                x=list(range(len(st.session_state.mem_data))),
                y=list(st.session_state.mem_data),
                name="Memory",
                line=dict(color='#00FFAA', width=3)
            )
            fig_mem.update_layout(
                yaxis=dict(range=[0, 100], title="Percentage"),
                xaxis=dict(title="Seconds Ago"),
                height=300,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_mem, use_container_width=True)
    
    # Refresh interval
    time.sleep(1.0)
