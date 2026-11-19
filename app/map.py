import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# run page: streamlit run "app/map.py"

# set path
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "data_clean_final" / "final_clean.csv"

# import data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    return df

df = load_data(data_path)

# title
with st.container(border=True):
    st.title("Map: explore the world")
    st.write("click on a country to see the data for that country")

# year selector
year = st.slider("year", min_value=int(df["year"].min()), max_value=int(df["year"].max()), value=2023)

# data for each selected year
year_data = df[df["year"] == year].copy()

# dummy column for map color
year_data["map_color"] = 1

# first version of the map (use px.choropleth -> match directly with the iso3 code)
fig = px.choropleth(
    year_data, 
    locations="iso3", 
    locationmode="ISO-3", 
    hover_name="country", 
    color="map_color", 
    color_continuous_scale=["#dce8b0", "#dce8b0"])

# remove color scale
fig.update_coloraxes(showscale=False)

# update the layout 
fig.update_geos(
    bgcolor="rgba(0,0,0,0)",
    showocean=True,
    oceancolor="#0e1117",
    showland=True,
    landcolor="#20242c",
    showcountries=True,
    countrycolor="#777777",
    coastlinecolor="#777777",
    showframe=False,
    projection_type="natural earth"
)

# transparent background (not white) and remove margins 
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

# display map and get selected country (hide toolbar)
with st.container(border=True):
    event = st.plotly_chart(fig, width="stretch", on_select="rerun", selection_mode="points", key="world_map", config={"displayModeBar": False})

st.write(event.selection)

# see how it looks --> very ugly in my opinion -> now a little better
# what can we improve:
# - different colors (green for country with data, grey for country with no data, yellow for selected country)
# - Better hover information (like country name and flag)
# - show country information cleanly in a separate container below the map
# - add country comparisons (continent or worldwide)