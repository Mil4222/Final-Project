import streamlit as st
import pandas as pd
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

# cacheing so the page doesn't have to constanly load

@st.cache_data
def load_data(path):
    """Read the dataset and return it as a DataFrame."""

    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    # NA remains text,so North America is not missing
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
        size="population",      
        size_max=40,            # size of the biggest dot
        hover_name="country",   # country name when hovering a dot
        labels={x: GEO_VARS[x], y: SOCIO_VARS[y], "population": "Population"},
    )
    st.plotly_chart(fig)
    st.caption("Dot size = population")

    print(df.columns.tolist())

# container 3: correlation
with st.container(border=True):
    if len(data) < 50:  # correlation makes no sense with too few countries
      st.warning("Fewer than 50 countries have data for this year. Try another year.")
    else:
# Pearson correlation between x and y
        r = data[x].corr(data[y])  
        st.metric("Correlation (r)", f"{r:.2f}")
        st.caption(f"n = {len(data)} countries in {year}")