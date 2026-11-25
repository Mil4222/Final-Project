import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# run page: streamlit run "app/map.py"

# idea for the map:
# user can select a year and a variable
# the map shows a color cradient (darker -> highest value)
# you can also click a country and see the specific value and a card with the worlds/continent ranking

# set path
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "data_clean_final" / "final_clean.csv"

# import data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    return df

df = load_data(data_path)

# style for settings container
st.markdown(
    """
    <style>
    .st-key-setting_card {
        background-color: #FFFDF7;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# set variables
map_vars = {
    "constant_gdp_capita": "GDP per capita (constant 2015 $US)",
    "hdi": "Human Development Index",
    "life_expectancy": "Life expectancy (years)",
    "urban_pop_perc": "Urban population (% of total population)",
    "pm2.5_pollution": "PM2.5 pollution (mean annual exposure)",
    "forest_ratio": "Forest coverage (% of total area)",
    "pop_density": "Population density",
    "mean_edu_year": "Average years of schooling",
    "population": "Population (M)",
    "unemployment_rate": "Unemployment rate (% of total labor force)",
    "median_age": "Median age (years)"
}

# title
with st.container(border=False):
    st.title("Map: explore the world")
    st.write("click on a country to see the data for that country")


# settings (select variable and year)
with st.container(border=True, key="setting_card"):
    
    cols = st.columns(2)
    with cols[0]: 
        # choose variable (display the values in the selectbox)
        select_label = st.selectbox("choose and indicator", options=list(map_vars.values())) 
        
        selected_var = next(
            key for key, value in map_vars.items()
            if value == select_label
        )

    with cols[1]:
        # choose year
        year = st.slider("choose a year", min_value=int(df["year"].min()), max_value=int(df["year"].max()), value=2023, help="Many indicators only cover 1990-2023")
        
    # data for each selected year
    year_data = df[df["year"] == year].copy()

    # population in millions
    year_data["population_m"] = year_data["population"] / 1_000_000

    # global rank
    year_data["world_rank"] = year_data[selected_var].rank(ascending=False, method="min")

    # continent rank
    year_data["continent_rank"] = (year_data.groupby("continent")[selected_var].rank(ascending=False, method="min"))

    # number of countries in the ranking
    world_tot = year_data[selected_var].notna().sum()
    year_data["continent_tot"] = (year_data.groupby("continent")[selected_var].transform(lambda x: x.notna().sum()))

# first version of the map (use px.choropleth -> match directly with the iso3 code)
# now I just chose random colors for the gradient -> can change later)
fig = px.choropleth(
    year_data, 
    locations="iso3", 
    locationmode="ISO-3", 
    hover_name="country", 
    color=selected_var, 
    color_continuous_scale=["#e2f2af","#c0d186","#97b17b","#76a273","#5c825f", "#597A57", "#405C3E"],
    )

# update the layout (random colors also here)
fig.update_geos(
    bgcolor="rgba(0,0,0,0)",
    showocean=True,
    oceancolor="#a7bde9",
    showland=True,
    landcolor="#d0d0d0",
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
with st.container(border=False):
    event = st.plotly_chart(fig, width="stretch", on_select="rerun", selection_mode="points", key="world_map", config={"displayModeBar": False})

# st.write(event.selection)

# what can we improve:
# - message for no data
# - Better hover information (like value with unit of measure) -> still figuring out how
# - add country comparisons/rankings in the cards
# - invert ranking for "bad" value like pollution
# - log the color for population and density 