import streamlit as st
import random
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import threading
import queue
import json

st.set_page_config(layout="wide", page_title="Smart Home Network Manager")

# Custom CSS for modern styling
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;zwe q2as
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 20px;
        color: #4CAF50;
    }
    .subheader {
        font-size: 1.2rem;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)

def mock_device_data():
    """
    Generate detailed fake data for device bandwidth simulation.
    """
    device_types = ['Smartphone', 'Laptop', 'Smart TV', 'Gaming Console', 'Tablet', 
                   'Security Camera', 'Smart Speaker', 'Desktop PC']
    manufacturers = ['Apple', 'Samsung', 'Sony', 'Microsoft', 'Google', 'Amazon', 'LG', 'Dell']
    activities = ['Streaming', 'Gaming', 'Web Browsing', 'Video Call', 'Download', 'Upload', 'IoT Communication']
    
    devices = []
    for i in range(random.randint(8, 15)):  # Random number of devices for realism
        device_type = random.choice(device_types)
        manufacturer = random.choice(manufacturers)
        activity = random.choice(activities)
        
        device = {
            "name": f"{manufacturer} {device_type}",
            "usage": random.randint(1, 1000),
            "priority": random.randint(1, 3),
            "activity": activity,
            "connected_since": (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime("%H:%M:%S"),
            "ip_address": f"192.168.1.{random.randint(2, 254)}",
            "signal_strength": random.randint(50, 100),
            "data_transferred": round(random.uniform(0.1, 10.0), 2)
        }
        devices.append(device)
    return devices

# Session state initialization
if 'real_time_data' not in st.session_state:
    st.session_state.real_time_data = queue.Queue()
    st.session_state.running = False
    st.session_state.current_devices = mock_device_data()
    st.session_state.historical_usage = []

def generate_historical_data(devices, hours=24):
    """Generate mock historical bandwidth usage data."""
    data = []
    for hour in range(hours):
        timestamp = datetime.now() - timedelta(hours=hours-hour)
        for device in devices:
            usage = random.randint(100, 1000)
            data.append({
                'timestamp': timestamp,
                'device': device['name'],
                'usage': usage
            })
    return pd.DataFrame(data)

def allocate_bandwidth(devices, total_bandwidth):
    """
    Dynamically allocates bandwidth with advanced prioritization.
    """
    # Priority multipliers based on activity type
    activity_multipliers = {
        'Video Call': 1.5,
        'Gaming': 1.3,
        'Streaming': 1.2,
        'Download': 1.0,
        'Upload': 1.0,
        'Web Browsing': 0.8,
        'IoT Communication': 0.5
    }
    
    # Sort devices by priority and adjusted usage
    for device in devices:
        device['adjusted_priority'] = (
            device['priority'] * 
            activity_multipliers.get(device['activity'], 1.0) * 
            (device['signal_strength'] / 100)
        )
    
    devices.sort(key=lambda d: (d['adjusted_priority'], -d['usage']), reverse=True)
    
    allocation = {}
    remaining_bandwidth = total_bandwidth
    
    for device in devices:
        if remaining_bandwidth <= 0:
            allocation[device['name']] = 0
        else:
            share = min(
                device['usage'] * device['adjusted_priority'],
                remaining_bandwidth
            )
            allocation[device['name']] = round(share, 2)
            remaining_bandwidth -= share
    
    return allocation

def update_real_time_data():
    """Background worker to update device data in real-time"""
    while st.session_state.running:
        devices = st.session_state.current_devices
        for device in devices:
            # Simulate realistic usage fluctuations
            usage_change = random.uniform(-50, 50)
            device['usage'] = max(0, min(1000, device['usage'] + usage_change))
            device['signal_strength'] = max(50, min(100, device['signal_strength'] + random.uniform(-5, 5)))
            device['data_transferred'] += round(random.uniform(0.01, 0.1), 2)
            
            # Randomly change activity sometimes
            if random.random() < 0.1:  # 10% chance to change activity
                device['activity'] = random.choice([
                    'Streaming', 'Gaming', 'Web Browsing', 'Video Call',
                    'Download', 'Upload', 'IoT Communication'
                ])
        
        # Update allocation
        allocation = allocate_bandwidth(devices, st.session_state.total_bandwidth)
        
        # Store historical data
        timestamp = datetime.now()
        st.session_state.historical_usage.append({
            'timestamp': timestamp,
            'devices': devices.copy(),
            'allocation': allocation.copy()
        })
        
        # Keep only last 24 hours of data
        cutoff_time = timestamp - timedelta(hours=24)
        st.session_state.historical_usage = [
            data for data in st.session_state.historical_usage 
            if data['timestamp'] > cutoff_time
        ]
        
        time.sleep(1)  # Update every second

def start_real_time_monitoring():
    """Start the real-time monitoring thread"""
    if not st.session_state.running:
        st.session_state.running = True
        thread = threading.Thread(target=update_real_time_data)
        thread.daemon = True
        thread.start()

def stop_real_time_monitoring():
    """Stop the real-time monitoring"""
    st.session_state.running = False

# Navigation
page = st.sidebar.selectbox(
    "Dashboard",
    ["Network Overview", "Real-time Monitoring", "Device Management", 
     "Historical Analysis", "Settings", "About"]
)

# Sidebar configurations
with st.sidebar:
    st.header("Network Settings")
    total_bandwidth = st.slider(
        "Total Bandwidth (Mbps):",
        min_value=100,
        max_value=1000,
        value=500,
        step=50
    )
    
    refresh_interval = st.slider(
        "Refresh Interval (sec):",
        min_value=5,
        max_value=60,
        value=10,
        step=5
    )
    
    st.markdown("---")
    st.markdown("### Network Status")
    st.metric(
        "Network Health",
        "Excellent",
        "\u2191 98% uptime"
    )

# Main content
if page == "Network Overview":
    st.markdown("<div class='header'>Network Overview</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Devices", "12", "\u2191 2 from yesterday")
    with col2:
        st.metric("Bandwidth Usage", f"{random.randint(60, 90)}%", "Normal load")
    with col3:
        st.metric("Network Speed", f"{random.randint(80, 95)} Mbps", "\u2191 5 Mbps")
    
    # Generate and process data
    devices = mock_device_data()
    allocation = allocate_bandwidth(devices, total_bandwidth)
    
    # Create bandwidth usage chart
    usage_data = pd.DataFrame({
        'Device': list(allocation.keys()),
        'Bandwidth': list(allocation.values())
    })
    
    fig = px.bar(
        usage_data,
        x='Device',
        y='Bandwidth',
        title='Real-time Bandwidth Allocation',
        color='Bandwidth',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Device table with modern styling
    st.markdown("### Connected Devices")
    device_df = pd.DataFrame(devices)
    st.dataframe(
        device_df[['name', 'activity', 'connected_since', 'signal_strength', 'data_transferred']],
        use_container_width=True
    )

elif page == "Real-time Monitoring":
    st.markdown("<div class='header'>Real-time Network Monitoring</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.running:
            if st.button("Start Real-time Monitoring"):
                st.session_state.total_bandwidth = total_bandwidth
                start_real_time_monitoring()
        else:
            if st.button("Stop Monitoring"):
                stop_real_time_monitoring()
    
    with col2:
        update_speed = st.slider(
            "Update Interval (seconds)",
            min_value=1,
            max_value=10,
            value=2
        )
    
    # Real-time metrics
    if st.session_state.running:
        placeholder = st.empty()
        chart_placeholder = st.empty()
        table_placeholder = st.empty()
        
        while st.session_state.running:
            with placeholder.container():
                # Current network metrics
                m1, m2, m3 = st.columns(3)
                total_usage = sum(d['usage'] for d in st.session_state.current_devices)
                active_devices = len([d for d in st.session_state.current_devices if d['usage'] > 0])
                
                m1.metric(
                    "Current Bandwidth Usage",
                    f"{round(total_usage/total_bandwidth * 100, 1)}%",
                    f"{round(total_usage, 1)} Mbps"
                )
                m2.metric(
                    "Active Devices",
                    active_devices,
                    f"{active_devices - len(st.session_state.current_devices)} from total"
                )
                m3.metric(
                    "Network Efficiency",
                    f"{round(random.uniform(90, 99), 1)}%",
                    "Optimal"
                )
            
            with chart_placeholder.container():
                # Real-time bandwidth allocation chart
                allocation = allocate_bandwidth(
                    st.session_state.current_devices,
                    total_bandwidth
                )
                
                fig = go.Figure()
                
                # Add bar chart for current usage
                fig.add_trace(go.Bar(
                    name='Current Usage',
                    x=list(allocation.keys()),
                    y=[d['usage'] for d in st.session_state.current_devices],
                    marker_color='lightblue'
                ))
                
                # Add bar chart for allocated bandwidth
                fig.add_trace(go.Bar(
                    name='Allocated Bandwidth',
                    x=list(allocation.keys()),
                    y=list(allocation.values()),
                    marker_color='royalblue'
                ))
                
                fig.update_layout(
                    title='Real-time Bandwidth Usage vs Allocation',
                    barmode='group',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True, key="realtime_chart")
            
            with table_placeholder.container():
                # Real-time device status table
                st.markdown("### Live Device Status")
                live_data = []
                for device in st.session_state.current_devices:
                    live_data.append({
                        'Device': device['name'],
                        'Activity': device['activity'],
                        'Current Usage (Mbps)': round(device['usage'], 1),
                        'Allocated (Mbps)': round(allocation[device['name']], 1),
                        'Signal': f"{round(device['signal_strength'])}%",
                        'Data Transferred (GB)': round(device['data_transferred'], 2)
                    })
                
                st.dataframe(
                    pd.DataFrame(live_data),
                    use_container_width=True,
                    height=400
                )
            
            time.sleep(update_speed)
            
    else:
        st.info("Click 'Start Real-time Monitoring' to begin live network analysis")
elif page == "Device Management":
    st.markdown("<div class='header'>Device Management</div>", unsafe_allow_html=True)
    
    # Device priority management
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Priority Devices")
        priority_devices = [d for d in mock_device_data() if d['priority'] == 3]
        for device in priority_devices:
            st.markdown(f"""
                <div class="metric-card">
                    <h4>{device['name']}</h4>
                    <p>Activity: {device['activity']}</p>
                    <p>Signal: {device['signal_strength']}%</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Network Map")
        # Create a network topology visualization
        devices = mock_device_data()
        fig = go.Figure()
        
        # Add router node
        fig.add_trace(go.Scatter(
            x=[0],
            y=[0],
            mode='markers+text',
            name='Router',
            marker=dict(size=20, symbol='star'),
            text=['Router'],
            textposition='bottom center'
        ))
        
        # Add device nodes
        x = [random.uniform(-1, 1) for _ in devices]
        y = [random.uniform(-1, 1) for _ in devices]
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers+text',
            name='Devices',
            marker=dict(size=10),
            text=[d['name'] for d in devices],
            textposition='top center'
        ))
        
        fig.update_layout(
            showlegend=False,
            title='Network Topology',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif page == "Historical Analysis":
    st.markdown("<div class='header'>Historical Network Analysis</div>", unsafe_allow_html=True)
    
    # Convert historical data to DataFrame
    if st.session_state.historical_usage:
        historical_df = pd.DataFrame([
            {
                'timestamp': entry['timestamp'],
                'device': device['name'],
                'usage': device['usage'],
                'allocated': entry['allocation'][device['name']]
            }
            for entry in st.session_state.historical_usage
            for device in entry['devices']
        ])
        
        # Create time series chart with both usage and allocation
        fig = go.Figure()
        
        for device in set(historical_df['device']):
            device_data = historical_df[historical_df['device'] == device]
            
            fig.add_trace(go.Scatter(
                x=device_data['timestamp'],
                y=device_data['usage'],
                name=f"{device} (Usage)",
                line=dict(dash='solid')
            ))
            
            fig.add_trace(go.Scatter(
                x=device_data['timestamp'],
                y=device_data['allocated'],
                name=f"{device} (Allocated)",
                line=dict(dash='dot')
            ))
        
        fig.update_layout(
            title='Historical Usage vs Allocation',
            xaxis_title='Time',
            yaxis_title='Bandwidth (Mbps)',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add usage statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Peak Usage Analysis")
            peak_usage = historical_df.groupby('timestamp')['usage'].sum()
            peak_time = peak_usage.idxmax()
            st.info(f"Peak network usage: {round(peak_usage.max(), 1)} Mbps at {peak_time.strftime('%H:%M:%S')}")
            
        with col2:
            st.markdown("### Device Statistics")
            device_stats = historical_df.groupby('device').agg({
                'usage': ['mean', 'max'],
                'allocated': ['mean', 'max']
            }).round(2)
            st.dataframe(device_stats)

        # Optional: Display raw historical data
        with st.expander("View Raw Historical Data"):
            st.dataframe(historical_df, use_container_width=True)
    else:
        st.info("No historical data available. Start real-time monitoring to collect data.")

           
elif page == "Settings":
    st.header("Settings")
    
    # User settings form
    with st.form("settings_form"):
        st.markdown("### General Settings")
        
        theme = st.radio("Select Theme", ["Light", "Dark"], index=0)
        language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German"])
        notifications = st.checkbox("Enable Notifications", value=True)
        
        st.markdown("### Bandwidth Settings")
        total_bandwidth = st.slider(
            "Adjust Total Bandwidth (Mbps):",
            min_value=100,
            max_value=1000,
            value=total_bandwidth,
            step=50
        )
        
        st.markdown("### Other Configurations")
        st.text_input("Admin Email Address", placeholder="admin@example.com")
        
        submitted = st.form_submit_button("Save Changes")
        if submitted:
            st.success("Settings have been saved successfully.")
    
    st.markdown("---")
    st.markdown("### Reset Dashboard")
    if st.button("Reset All Settings"):
        st.warning("All settings have been reset to default.")
        st.experimental_rerun()

elif page == "About":
    st.header("About")
    
    st.markdown("""
    ## Smart Home Network Manager
    The **Smart Home Network Manager** is a modern dashboard designed to optimize and monitor your home network in real time. It provides an intuitive and user-friendly interface with advanced features such as:
    
    - **Real-time Monitoring:** Track bandwidth usage and allocation dynamically.
    - **Device Management:** View and manage connected devices with activity insights.
    - **Historical Analysis:** Visualize past network usage trends and peak times.
    - **Custom Settings:** Tailor bandwidth limits, update intervals, and dashboard themes to your preferences.
    
    ### Key Features:
    - **Modern UI:** Built with responsive and elegant design principles.
    - **Dynamic Bandwidth Allocation:** Ensures prioritized allocation based on device activity and priority.
    - **Detailed Metrics:** Provides insights into signal strength, data transferred, and real-time device activities.
    
    ### Technologies Used:
    - **Streamlit** for a streamlined and interactive web application.
    - **Plotly** for dynamic and interactive data visualizations.
    - **Python** for robust backend processing.
    
    ### About the Developer:
    This project was designed to simplify network management for modern smart homes. If you have suggestions, feel free to contact me through the feedback section in the dashboard.
    ### Feedback:
    If you have any feedback or suggestions, please feel free to reach out to me.

    ### License:
    This project is licensed under the MIT License.

    ### Contact:
    For any inquiries or support, please contact me at [raghavareddy696969@gmail.com].

    ### Acknowledgments:
    - Special thanks to the open-source community for their contributions and support.
    ---
    *Version 1.0.0 - Last Updated: 2024*
    """)
