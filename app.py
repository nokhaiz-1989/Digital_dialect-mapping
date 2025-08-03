import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import json
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ✅ Set Streamlit page config FIRST
st.set_page_config(
    page_title="Digital Dialectal Mapper",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🗺️ Digital Dialectal Mapper for Urdu")

# Load dialect sample data
@st.cache_data
def load_data():
    file_path = os.path.join("data", "dialect_samples.csv")
    if not os.path.exists(file_path):
        st.error("CSV file not found. Make sure 'dialect_samples.csv' is in the 'data' folder.")
        return pd.DataFrame()
    return pd.read_csv(file_path)

data = load_data()

# Load dialect regions GeoJSON
@st.cache_data
def load_geojson():
    file_path = os.path.join("data", "dialect_regions.geojson")
    if not os.path.exists(file_path):
        st.error("GeoJSON file not found. Make sure 'dialect_regions.geojson' is in the 'data' folder.")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

geojson = load_geojson()

# Map Rendering
if geojson:
    st.subheader("🗺️ Urdu Dialect Map")
    m = folium.Map(location=[30.3753, 69.3451], zoom_start=5)

    folium.GeoJson(
        geojson,
        name="geojson",
        tooltip=folium.GeoJsonTooltip(fields=["dialect", "region"])
    ).add_to(m)

    st_data = st_folium(m, width=1000, height=500)

# Data Table Display
if not data.empty:
    st.subheader("📄 Dialect Samples")
    st.dataframe(data)

    # Sidebar filters and stats
    st.sidebar.title("📊 Token & Collocate Stats")

    selected_dialect = st.sidebar.selectbox("Choose a Dialect", data["dialect"].unique())

    if selected_dialect:
        dialect_data = data[data["dialect"] == selected_dialect]
        tokens = " ".join(dialect_data["text"].astype(str)).split()
        token_counts = Counter(tokens)
        top_tokens = token_counts.most_common(20)

        # Display token frequency as bar chart
        token_df = pd.DataFrame(top_tokens, columns=["Token", "Frequency"])
        fig = px.bar(token_df, x="Token", y="Frequency", title=f"Top Tokens in {selected_dialect}")
        st.sidebar.plotly_chart(fig)

        # Generate and show word cloud
        wordcloud = WordCloud(width=400, height=300, background_color="white").generate(" ".join(tokens))
        st.sidebar.image(wordcloud.to_array(), use_column_width=True)

else:
    st.warning("No data available to display. Please upload valid CSV and GeoJSON files.")
