import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({
    'text.color': 'black',
    'axes.labelcolor': 'black',
    'axes.titlecolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black'
})

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airline Executive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Professional Airline Analytics Dashboard v2.0"}
)

# ── External CSS Loader ───────────────────────────────────────────────────────
def local_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

local_css("file.css")

st.title("✈️ Airline Executive Insights Dashboard")

# Add subtitle with professional styling
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='color: #0099cc; font-size: 1.15rem; font-weight: 600;'>
        📊 Real-time Analytics & Performance Monitoring
    </p>
</div>
""", unsafe_allow_html=True)

# ── Helper Function to Format Large Numbers ───────────────────────────────────
def format_currency(value):
    """Format large currency values in a readable way"""
    if value >= 10000000:  # >= 1 Crore
        return f"₹{value/10000000:.2f} Cr"
    elif value >= 100000:  # >= 1 Lakh
        return f"₹{value/100000:.2f} L"
    else:
        return f"₹{int(value):,}"

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_airline_dataset.csv")

    # Normalize column names to lowercase
    df.columns = df.columns.str.strip().str.lower()

    # Map total_stops to numeric
    stop_map = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
                'non-stop': 0, '1 stop': 1, '2 stop': 2, '3 stop': 3, '4 stop': 4,
                0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
    if 'total_stops' in df.columns:
        df['total_stops_num'] = df['total_stops'].map(stop_map).fillna(0).astype(int)

    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔍 Dashboard Filters")
st.sidebar.markdown("---")

# Airline filter
airline_options = ['All Airlines'] + sorted(df['airline'].dropna().unique().tolist())
selected_airlines = st.sidebar.multiselect("Select Airline(s)", airline_options, default=['All Airlines'])

# Source & Destination
source_options = sorted(df['source_city'].dropna().unique().tolist())
dest_options   = sorted(df['destination_city'].dropna().unique().tolist())

selected_source = st.sidebar.selectbox("Source City", source_options)
selected_dest   = st.sidebar.selectbox("Destination City", dest_options)

# Class filter
class_options = ['All Classes'] + sorted(df['class'].dropna().unique().tolist())
selected_class = st.sidebar.selectbox("Travel Class", class_options)

# Days Left filter
st.sidebar.markdown("")
days_options = ['All Days'] + sorted(df['days_left'].dropna().unique().tolist())
selected_days = st.sidebar.selectbox("Days Until Departure", days_options)

# ── Validate Selection ────────────────────────────────────────────────────────
if not selected_airlines:
    st.markdown("""
<div style="
    background: rgba(255, 193, 7, 0.15);
    border-left: 5px solid #ffc107;
    padding: 12px;
    border-radius: 10px;
    color: black;
    font-weight: 600;
">
⚠️ Please select at least one airline from the sidebar.
</div>
""", unsafe_allow_html=True)

if selected_source == selected_dest:
    st.markdown("""
<div style="
    background: rgba(255, 193, 7, 0.15);
    border-left: 5px solid #ffc107;
    padding: 12px;
    border-radius: 10px;
    color: black;
    font-weight: 600;
">
⚠️ Source and Destination cities are the same. Please choose different cities.
</div>
""", unsafe_allow_html=True)
    st.stop()

# ── Apply Airline Filter ──────────────────────────────────────────────────────
if 'All Airlines' in selected_airlines:
    airline_df = df.copy()
else:
    airline_df = df[df['airline'].isin(selected_airlines)]

# ── Apply Class Filter ────────────────────────────────────────────────────────
if selected_class != 'All Classes':
    airline_df = airline_df[airline_df['class'] == selected_class]

# ── Apply Days Left Filter ────────────────────────────────────────────────────
if selected_days != 'All Days':
    airline_df = airline_df[airline_df['days_left'] == selected_days]

# ── Section 1: Overall KPIs for Selected Airline(s) ──────────────────────────
airline_label = "All Airlines" if 'All Airlines' in selected_airlines else ", ".join(selected_airlines)
st.markdown(f'<div class="section-title">📊 Key Metrics — {airline_label}</div>', unsafe_allow_html=True)

if airline_df.empty:
    st.error("No data found for the selected filters.")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Flights",    f"{airline_df.shape[0]:,}")
col2.metric("Total Revenue",    format_currency(airline_df['price'].sum()))
col3.metric("Avg Price",        format_currency(airline_df['price'].mean()))
col4.metric("Min Price",        format_currency(airline_df['price'].min()))
col5.metric("Max Price",        format_currency(airline_df['price'].max()))

st.markdown("---")

# ── Section 2: Route-Specific KPIs ───────────────────────────────────────────
route_df = airline_df[
    (airline_df['source_city'] == selected_source) &
    (airline_df['destination_city'] == selected_dest)
]

st.markdown(f'<div class="section-title">🛫 Route Metrics — {selected_source} → {selected_dest}</div>', unsafe_allow_html=True)

if route_df.empty:
    st.warning(f"No flights found from **{selected_source}** to **{selected_dest}** for the selected airline/class.")
else:
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Flights on Route",  f"{route_df.shape[0]:,}")
    r2.metric("Route Revenue",     format_currency(route_df['price'].sum()))
    r3.metric("Avg Route Price",   format_currency(route_df['price'].mean()))
    r4.metric("Min Route Price",   format_currency(route_df['price'].min()))
    r5.metric("Max Route Price",   format_currency(route_df['price'].max()))

    # Avg duration on route
    if 'duration' in route_df.columns:
        avg_dur = route_df['duration'].mean()
        st.caption(f"⏱️ Average flight duration on this route: **{avg_dur:.2f} hrs**")

st.markdown("---")

# ── Section 3: Charts ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Visual Analysis</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Avg Price by Airline
with chart_col1:
    st.markdown("<h2 style='color:black;'>💰 Avg Price by Airline</h2>",unsafe_allow_html=True)
    avg_by_airline = airline_df.groupby('airline')['price'].mean().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    fig1.patch.set_facecolor('#f8f9fa')
    bars = ax1.barh(avg_by_airline.index, np.asarray(avg_by_airline.values), 
                     color=["#00d4ff", '#0099cc', '#007fa3', '#005580', '#003d5c'][:len(avg_by_airline)])
    ax1.set_xlabel("Average Price (₹)", fontsize=11, fontweight=600, color='#000000')
    ax1.set_title("Average Ticket Price by Airline", fontsize=12, fontweight=700, color='#000000', pad=15)
    ax1.set_facecolor('#f7f9fc')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#e0e6f2')
    ax1.spines['bottom'].set_color('#e0e6f2')
    ax1.tick_params(colors='#0099cc', labelsize=10)
    for label in ax1.get_xticklabels():
        label.set_fontweight('bold')
    for bar, val in zip(bars, avg_by_airline.values):
        ax1.text(val + 100, bar.get_y() + bar.get_height()/2, format_currency(val), 
                va='center', fontsize=9, fontweight=600, color='#0099cc')
    ax1.grid(axis='x', alpha=0.2, linestyle='--', color='#00d4ff')
    plt.tight_layout()
    st.pyplot(fig1, use_container_width=True)
    plt.close()

# Chart 2: Price Distribution
with chart_col2:
    st.markdown("<h2 style='color:black;'>📉 Price Distribution</h2>", unsafe_allow_html=True)
    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    fig2.patch.set_facecolor('#f7f9fc')
    ax2.hist(airline_df['price'], bins=40, color='#00d4ff', edgecolor='white', alpha=0.85)
    ax2.axvline(airline_df['price'].mean(), color='#ff6b6b', linestyle='--', linewidth=2.5, 
                label=f"Mean: {format_currency(airline_df['price'].mean())}")
    ax2.set_xlabel("Price (₹)", fontsize=11, fontweight=600, color='#000000')
    ax2.set_ylabel("Frequency", fontsize=11, fontweight=600, color='#000000')
    ax2.set_title("Ticket Price Distribution", fontsize=12, fontweight=700, color='#000000', pad=15)
    ax2.set_facecolor('#f7f9fc')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#e0e6f2')
    ax2.spines['bottom'].set_color('#e0e6f2')
    ax2.tick_params(colors='#0099cc', labelsize=10)
    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontweight('bold')
    ax2.legend(fontsize=10, loc='upper right', framealpha=0.9)
    ax2.grid(axis='y', alpha=0.2, linestyle='--', color='#00d4ff')
    plt.tight_layout()
    st.pyplot(fig2, use_container_width=True)
    plt.close()

chart_col3, chart_col4 = st.columns(2)

# Chart 3: Flights by Departure Time
with chart_col3:
    st.markdown("<h2 style = 'color:black;'>🕐 Flights by Departure Time</h2>", unsafe_allow_html=True)
    dep_counts = airline_df['departure_time'].value_counts()
    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    fig3.patch.set_facecolor('#f7f9fc')
    colors_pie = ['#00d4ff', '#0099cc', '#007fa3', '#005580', '#003d5c', '#00d4ff', '#0099cc']
    pie_result = ax3.pie(np.asarray(dep_counts.values), labels=dep_counts.index.tolist(), 
                          autopct='%1.1f%%', colors=colors_pie[:len(dep_counts)], 
                          startangle=140, textprops={'fontsize': 10, 'weight': 'bold'})
    ax3.set_title("Departure Time Distribution", fontsize=12, fontweight=700, color='#000000', pad=15)
    if len(pie_result) >= 3:
        autotexts = pie_result[2]
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
    plt.tight_layout()
    st.pyplot(fig3, use_container_width=True)
    plt.close()

# Chart 4: Avg Price by Class
with chart_col4:
    st.markdown("<h2 style='color:black;'>💎 Avg Price by Travel Class</h2>", unsafe_allow_html=True)
    class_avg = airline_df.groupby('class')['price'].mean().sort_values(ascending=False)
    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    fig4.patch.set_facecolor('#f7f9fc')
    bars = ax4.bar(class_avg.index, np.asarray(class_avg.values), 
                   color=['#00d4ff', '#0099cc', '#007fa3'][:len(class_avg)], edgecolor='white', linewidth=2)
    ax4.set_ylabel("Average Price (₹)", fontsize=11, fontweight=600, color='#000000')
    ax4.set_title("Average Ticket Price by Class", fontsize=12, fontweight=700, color='#000000', pad=15)
    ax4.set_facecolor('#f7f9fc')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_color('#e0e6f2')
    ax4.spines['bottom'].set_color('#e0e6f2')
    ax4.tick_params(colors='#0099cc', labelsize=10)
    for label in ax4.get_xticklabels() + ax4.get_yticklabels():
        label.set_fontweight('bold')
    for i, (bar, val) in enumerate(zip(bars, class_avg.values)):
        ax4.text(bar.get_x() + bar.get_width()/2, val + 200, format_currency(val), 
                ha='center', fontsize=10, fontweight=600, color='#0099cc')
    ax4.grid(axis='y', alpha=0.2, linestyle='--', color='#00d4ff')
    plt.tight_layout()
    st.pyplot(fig4, use_container_width=True)
    plt.close()

st.markdown("---")

# ── Section 4: Raw Data Table ─────────────────────────────────────────────────
st.markdown('<h2 style="color:black;">🗃️ Detailed Data Explorer</h2>', unsafe_allow_html=True)
with st.expander("📋 View Filtered Raw Data", expanded=True):
    display_df = route_df if not route_df.empty else airline_df
    
    # Display data info
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.metric("Rows", f"{display_df.shape[0]:,}")
    with col_info2:
        st.metric("Columns", display_df.shape[1])
    
    # Display dataframe with custom styling
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=400)
    
    # Download button
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name="filtered_airline_data.csv",
        mime="text/csv"
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #8892b0; font-size: 0.9rem;'>
    <p>✈️ <strong>Airline Executive Insights Dashboard v2.0</strong></p>
    <p>Powered by Streamlit | Data Analytics & Visualization Platform</p>
    <p style='font-size: 0.85rem; margin-top: 1rem;'>© 2026 - All Rights Reserved | Last Updated: April 2026</p>
</div>
""", unsafe_allow_html=True)
