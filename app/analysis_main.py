import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from pathlib import Path

DATA_PATH= DATA_PATH = Path(__file__).parent.parent / "data" / \
    "data_clean_final" / "final_clean.csv"

# defining GEO and SE variables

# GEO - facts about location
GEO_VARS={
    "distance_equator": "Distance from equator (° latitude)", 
    "area_sq_km": "Land area (km²)",
    "pop_density": "Population density (people per km²)",
    "forest_ratio": "Forest coverage (% of land area)",}

# SE - how people live (population is left out because it will show through size of the dot)
SOCIO_VARS = {
    "gdp_capita": "GDP per capita (US$)",
    "hdi": "Human Development Index (0-1)",
    "life_expectancy": "Life expectancy (years)",
    "unemployment_rate": "Unemployment rate (%)",
    "urban_pop_perc": "Urban population (% of total)",
    "median_age": "Median age (years)",
    "secondary_edu_years": "Secondary education (years)"}

CONTINENTS = {
    "AF": "Africa",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "North America",  
    "SA": "South America",
    "OC": "Oceania",
}

# cacheing so the page doesn't have to constanly load

@st.cache_data
def load_data(path):
    """Read the dataset and return it as a DataFrame."""

    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    # NA remains text,so North America is not missing

    df["continent_name"] = df["continent"].map(CONTINENTS)
    return df


df = load_data(DATA_PATH)  # load data (from cache after the first time)

# page tittle

st.title("Does the map predict the numbers?")
st.caption("Pick a geographic variable and a socioeconomic one. "
           "Every dot is a country.")

# container 1

with st.container(border=True):
    col1, col2, col3 = st.columns(3)

# dropdown 1 - GEO
with col1:
     x = st.selectbox( "Geography (x-axis)",options=list(GEO_VARS.keys()),
                      format_func=GEO_VARS.get,)

# dropdown 2 - SOCIOECON
with col2:
        y = st.selectbox("Socioeconomic (y-axis)", options=list(SOCIO_VARS.keys()),
            format_func=SOCIO_VARS.get)

# dropdown 3 - YEARS
years = sorted(df["year"].unique())
with col3:
        year = st.select_slider("Year",options=years,
            value=2020 if 2020 in years else years[-1],) 
        # slider starting point


# container 2: scatter plot

# keep one year, and only countries that have x, y AND population
data = df[df["year"] == year].dropna(subset=[x, y, "population"])


with st.container(border=True):
    fig = px.scatter(
        data,
        x=x,
        y=y,
        color="continent_name",  
        size="population",       
        size_max=40,             
        hover_name="country",    
        labels={x: GEO_VARS[x], y: SOCIO_VARS[y],
                "population": "Population", "continent_name": "Continent"},
    )

    # red trend line (only if there are enough countries)
    if len(data) >= 50:
        # find the straight line that fits the dots best: y = slope * x + intercept
        slope, intercept = np.polyfit(data[x], data[y], 1)

        # the line only needs two points: leftmost and rightmost x
        x_line = np.array([data[x].min(), data[x].max()])
        y_line = slope * x_line + intercept

        fig.add_scatter(
            x=x_line,
            y=y_line,
            mode="lines",                           # a line, not dots
            line=dict(color="red", dash="dash"),    # red and dashed
            name="Trend",                           # name in the legend
        )

    st.plotly_chart(fig)
    st.caption("Dot size = population · dashed red line = trend")

# container 3: correlation
with st.container(border=True):
    if len(data) < 50:  # correlation makes no sense with too few countries
      st.warning("Fewer than 50 countries have data for this year. Try another year.")
    else:
# Pearson correlation between x and y
        r = data[x].corr(data[y])  
        st.metric("Correlation (r)", f"{r:.2f}")
        st.caption(f"n = {len(data)} countries in {year}")