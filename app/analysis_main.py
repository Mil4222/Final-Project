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
    "constant_gdp_capita": "GDP per capita (US$)",
    "hdi": "Human Development Index (0-1)",
    "life_expectancy": "Life expectancy (years)",
    "unemployment_rate": "Unemployment rate (%)",
    "urban_pop_perc": "Urban population (% of total)",
    "median_age": "Median age (years)",
    "secondary_edu_years":"Secondary schooling (years)"}

# removed secondary edu years: the variable described the offical length, not how eduacated people are

# after running the first trial:
# there were some skewed variables: few huge values, most small ones
# solution: show on a log scale so all countries get space

LOG_VARS = ["area_sq_km", "pop_density", "constant_gdp_capita"]

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



# keep one year, and only countries that have x, y AND population
data = df[df["year"] == year].dropna(subset=[x, y, "population"])

# should x or y use a log scale?
log_x = x in LOG_VARS  
log_y = y in LOG_VARS

# log of 0 or negative numbers is impossible, so drop those rows
if log_x:
    data = data[data[x] > 0]
if log_y:
    data = data[data[y] > 0]

# the values used for trend line and correlation:
# logged if the axis is logged, otherwise the normal values
x_vals = np.log10(data[x]) if log_x else data[x]
y_vals = np.log10(data[y]) if log_y else data[y]

# container 2: scatter plot

with st.container(border=True):
    fig = px.scatter(
        data,
        x=x,
        y=y,
        color="continent_name",  # one colour per continent
        size="population",       # bigger dot = more people
        size_max=40,             # size of the biggest dot
        hover_name="country",    # country name when hovering a dot
        log_x=log_x,             # log scale on x if needed
        log_y=log_y,             # log scale on y if needed
        labels={x: GEO_VARS[x], y: SOCIO_VARS[y],
                "population": "Population", "continent_name": "Continent"},
    )

    # red trend line (only if there are enough countries)
    if len(data) >= 50:
        # y= ax+b
        slope, intercept = np.polyfit(x_vals, y_vals, 1)

        # two endpoints are sufficent
        x_line = np.array([x_vals.min(), x_vals.max()])
        y_line = slope * x_line + intercept

        # undo the log so the line sits on the right spot on the axis
        if log_x:
            x_line = 10 ** x_line
        if log_y:
            y_line = 10 ** y_line

        fig.add_scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            line=dict(color="red", dash="dash"),
            name="Trend",
        )

    st.plotly_chart(fig)
    st.caption("Dot size = population · dashed red line = trend")

# -----------------------------
# container 3: correlation, outliers, info card
# -----------------------------

col_corr, col_out, col_card = st.columns(3)

# card 1: correlation
with col_corr:
    with st.container(border=True, height=300):
        st.caption("WHAT THIS SHOWS")
        if len(data) < 50:  # correlation makes no sense with too few countries
            st.warning("Fewer than 50 countries have data for this year. "
                       "Try another year.")
        else:
            r = x_vals.corr(y_vals)  # Pearson correlation (on logged values if log scale)
            st.metric("Correlation (r)", f"{r:.2f}")
            st.caption(f"n = {len(data)} countries in {year}")

            if log_x or log_y:
                st.caption("Log scale used for skewed variables; "
                           "correlation is calculated on the logged values.")

# card 2: biggest outliers = the 3 countries furthest from the trend line
with col_out:
    with st.container(border=True, height=300):
        st.caption("BIGGEST OUTLIERS")
        if len(data) < 50:
            st.caption("Not enough countries for an outlier analysis.")
        else:
            top = data.sort_values("z", key=abs, ascending=False).head(3)
            for _, row in top.iterrows():
                side = "above" if row["z"] > 0 else "below"
                st.markdown(f"**{row['country']}**: {row[y]:,.1f}, {side} "
                            f"the trend (predicted {row['expected']:,.1f})")

# card 3: selected country (stays until another dot is clicked)
with col_card:
    with st.container(border=True, height=300):
        if country is None:
            st.caption("SELECTED COUNTRY")
            st.info("Click a dot on the chart (or search above).")
        else:
            st.caption(country.upper())
            row = df[(df["year"] == year) & (df["country"] == country)]
            if row.empty:
                st.warning(f"No data for {country} in {year}.")
            else:
                row = row.iloc[0]
                st.markdown(f"{GEO_VARS[x]}: **{row[x]:,.1f}**  \n"
                            f"{SOCIO_VARS[y]}: **{row[y]:,.1f}**")
                in_chart = data[data["country"] == country]
                if len(data) >= 50 and not in_chart.empty:
                    point = in_chart.iloc[0]
                    side = "above" if point["z"] > 0 else "below"
                    st.markdown(f"{country} sits **{side}** the trend: countries "
                                f"like it are predicted to have "
                                f"{point['expected']:,.1f}.")
                elif in_chart.empty:
                    st.caption("Not on the chart: some values are missing this year.")
 