# do we want to install watchdog?
# streamlit run app/page_skeleton.py
# page explanation: x-axis is a year slider.
# y-axis will be variables users can choose from. historical tren per country
# ========================================================================================================================

# -----------------
# import
# -----------------
import pandas as pd
from pathlib import Path
import plotly.express as px
import streamlit as st

# !test line: shows whether this file is executed at all
st.write("line_plot.py is running")

# -----------------
# settings for page
# -----------------

DATA_PATH = Path(__file__).parent.parent / "data" / \
    "data_clean_final" / "final_clean.csv"
# not absolute path for compatibiliy reason
# path built from where code file is not dependent on terminal or computer

# ----------------------------------------------------------------------
# variables settings y-axis
# Key = column names, value = readable name
# left out variables if no variance in time (area, distance, coordinates)
# variables looked up from notebook
# ----------------------------------------------------------------------

VARIABLES = {
    "life_expectancy": "Life expectancy (years)",  # life expectancy at birth
    # ! income per person in dollars, not inflation adjusted
    "constant_gdp_capita": "GDP per capita (constant 2015 US$)",
    # ! duration by law ?
    "mean_edu_year": "Average schooling (years)",
    "hdi": "Human Development Index (0–1)",  # UNDP HDI
    # share of the labour force without a job
    "unemployment_rate": "Unemployment rate (%)",
    # share of people living in cities
    "urban_pop_perc": "Urban population (% of total)",
    # yearly growth of the urban population
    "urban_pop_growth": "Urban population growth (% per year)",
    # fine-particle air pollution
    "pm2.5_pollution": "PM2.5 air pollution (µg/m³)",
    # share of land covered by forest
    "forest_ratio": "Forest cover (% of land area)",
    # half the population is older, half is younger
    "median_age": "Median age (years)",
    # people per square kilometre
    "pop_density": "Population density (people per km²)",
    "population": "Population",  # total number of people
    "urban_pop_total": "Urban population",  # number of people living in cities
    # number of people living in rural areas
    "rural_population": "Rural population",
}

# ----------------------------------------------
# define full names for continent abbreviations
# ----------------------------------------------

CONTINENTS = {
    "AF": "Africa",
    "AS": "Asia",
    "EU": "Europe",
    # code NA (careful: pandas would read "NA" as missing, see load_data)
    "NA": "North America",
    "SA": "South America",
    "OC": "Oceania",
}

# ---------------------------------
# default settings when page opens
# ---------------------------------

DEFAULT_COUNTRIES = ["Switzerland", "Italy",
                     "Croatia", "India", "Brazil", "Nigeria"]

# -------------------
# load the data
# -------------------


@st.cache_data
def load_data(path):
    """Read the dataset and return it as a DataFrame."""

    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    # NA remains text, so North America and Namibia don't evaluate to false, empty values remain NA
    df["continent_name"] = df["continent"].map(CONTINENTS)
    # added column with full continent names
    return df


df = load_data(DATA_PATH)

# ----------------
# page title
# ----------------

with st.container(border=False):  # NO framed box for title
    st.title("Trends over time")
    st.caption(  # subtitle
        "Choose a variable, a country and a time span to see how they developed.")

# ----------------------
# conatiner for settings
# ----------------------

# all years in the data, ascending (1960 ... 2025)
years = sorted(df["year"].unique())
countries = sorted(df["country"].unique())  # all country names, A to Z

with st.container(border=False):  # NON framed box that holds all controls
    st.subheader("Settings")  # heading inside the box

    # two columns; the right one is twice as wide
    col1, col2 = st.columns([1, 2])

    with col1:  # left column
        variable = st.selectbox(  # dropdown for the y-axis variable
            "Variable (y-axis)",  # label above the dropdown
            # the column names are the options...
            options=list(VARIABLES.keys()),
            # ...but the readable names are shown
            format_func=lambda col: VARIABLES[col],
            key="line_variable",  # unique ID of this widget
        )
        mode = st.radio(  # choose between single countries and continent averages (EU e.g.)
            "Show",  # label
            ["Countries", "Continent averages"],  # the two options
            horizontal=True,  # options next to each other
            key="line_mode",  # unique ID
        )
        show_world = st.checkbox(    # tick box for world average
            "World Average ",
            value=True,
            key="line_world",
        )

    with col2:  # right column
        # ≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠
        # by adding this code, user has a toggle to reverse the sorting Z-A instead A-Z
        # reverse_order = st.toggle(  # on/off switch for the sorting direction
        #     "Sort countries Z → A",  # label next to the switch
        #     value=False,  # off at the start, so the list is A → Z
        #     key="line_sort_desc",  # unique ID (starts with "line_" like all widgets on this page)
        # )
        # countries = sorted(df["country"].unique(), reverse=reverse_order)  # A-Z when off, Z-A when on
        # can be added to any sorting ( legend, dataframe, ...)
       # ≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠≠

        selected_countries = st.multiselect(  # dropdown where several countries can be picked
            "Countries",  # label
            options=countries,  # all countries
            # pre-select those that exist
            default=[c for c in DEFAULT_COUNTRIES if c in countries],
            # greyed out when continents are shown
            disabled=(mode == "Continent averages"),
            key="line_countries",  # unique ID
        )
        year_range = st.slider(  # slider with two both ends moveable
            "Years (x-axis)",  # label
            min_value=int(years[0]),  # earliest year in the data
            max_value=int(years[-1]),  # latest year in the data
            # start range: 1990 until the latest year
            value=(1990, int(years[-1])),
            step=1,  # move in steps of one year
            key="line_years",  # unique ID
        )

# ---------------
# data for chart
# ---------------

start, end = year_range  # unpack the two slider values into start year and end year
# keep only the years in the chosen span
in_range = df[(df["year"] >= start) & (df["year"] <= end)]

if mode == "Countries":  # one line per country
    plot_data = in_range[in_range["country"].isin(
        selected_countries)]  # keep the selected countries
    line_col = "country"  # draw one line per country
else:  # one line per continent
    plot_data = (  # compute the average of each continent in each year
        in_range.groupby(["continent_name", "year"], as_index=False)[
            variable]  # group by continent and year
        .mean()  # unweighted mean over the countries in the group ?? ( not sure)
    )
    line_col = "continent_name"  # draw one line per continent

# ---------
# create world verage
# --------------
if show_world:
    world = in_range.groupby("year", as_index=False)[variable].mean()
    world[line_col] = "World Average"
    # part of other lines in chart
    plot_data = pd.concat([plot_data, world], ignore_index=True)


# do NOT drop missing values: Plotly breaks the line where a value is missing,
# so gaps in the data become visible jumps in the chart
# True if at least one value exists in the selection
has_data = plot_data[variable].notna().any()

# -------------------------------
# container for the chart
# -------------------------------

with st.container(border=False):  # framed box for the chart
    # ! chart title: variable and time span, do we want to keep it like this
    st.subheader(f"{VARIABLES[variable]}, {start}–{end}")

    if not has_data:  # no value at all in this selection?
        # tell the user
        st.info(
            "No data for this selection. Pick other countries or a later time span.")
    else:  # there is data: draw the chart
        # sort by line and year so each line runs left to right
        plot_data = plot_data.sort_values([line_col, "year"])
        fig = px.line(  # create a line chart
            plot_data,  # the prepared data, missing values included
            x="year",  # years on the x-axis
            y=variable,  # chosen variable on the y-axis
            color=line_col,  # one coloured line per country or continent
            markers=True,  # a dot on every data point
            labels={  # readable names for axes and legend
                "year": "Year",  # x-axis title
                # !y-axis title, therefore kind of interactive
                variable: VARIABLES[variable],
                "country": "Country",  # legend title (countries)
                "continent_name": "Continent",  # legend title (continents)
            },
        )
        # make sure missing years stay as gaps (no bridging line)
        fig.update_traces(connectgaps=False)
        fig.update_traces(selector=dict(name="World Average"), line=dict(
            color="black", dash="dash"))  # specification how world average line should look

        # hovering shows all lines' values for that year at once; hover over plot and see all countries
        fig.update_layout(hovermode="x unified")
        # show the chart on the page, with built in features
        st.plotly_chart(fig, key="line_chart")

        # rows with a real value (only used for the caption)
        valid = plot_data.dropna(subset=[variable])
        # first year with data in the selection
        first_year = int(valid["year"].min())
        # last year with data in the selection
        last_year = int(valid["year"].max())
        st.caption(  # small grey text under the chart: coverage, gaps and source
            f"Data shown from {first_year} to {last_year}. Gaps in a line mean missing data for those years. "
            "Continent averages are unweighted means across countries. "
            "Source: World Bank WDI, UNDP Human Development Report."
        )

# --------------------------
# notes under chart
# --------------------------

with st.container(border=True):  # framed box for the interpretation
    # line 1: describe
    st.markdown("**What you see:** how the chosen variable developed over time.")
    # line 2: the point
    st.markdown(
        "**Why it matters:** trends show whether gaps between countries are closing or widening.")
    # line 3: limits
    st.markdown(
        "**Caveat:** some variables start late (HDI from 1990, unemployment from 1991).")
