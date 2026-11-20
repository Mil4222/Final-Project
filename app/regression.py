import pandas as pd
import streamlit as st
import statsmodels.formula.api as smf
from pathlib import Path
import numpy as np

# run page: streamlit run "app/regression.py"

# idea: since some variables have no within country change over the years (area, distance form equator,..)
# make two separate models: 
# - cross-sectional: compares countries in one selected year -> choose controls, SD (classic, robust) and year, maybe continent
# - panel: analyze changes within countries across years -> choose controls, SD (classic, robust, clustered by country), FE (year, country)
# For now i would just allow preset questions, not complete freedom for the user
# still allow some freedom with control choices and SD methods
# important: choose questions that make sense 


# set path
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "data_clean_final" / "final_clean.csv"

# import data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    return df

df = load_data(data_path)

st.set_page_config(layout="wide")

# rename pollution because it causes problems in the mddel
df = df.rename(columns={"pm2.5_pollution": "pm25_pollution"})

# create log variables (i checked -> no zeros and negative)
df["log_gdp_capita"] = np.log(df["gdp_capita"])
df["log_area_sq_km"] = np.log(df["area_sq_km"])
df["log_population"] = np.log(df["population"])
df["log_pop_density"] = np.log(df["pop_density"])

# possible variables cross
cross_vars = {
    "log_gdp_capita": "GDP per capita (current $US)",
    "distance_equator": "Distance from the equator",
    "hdi": "Human Developement Index (HDI)",
    "urban_pop_perc": "Urban population (%)",
    "log_population": "Total population",
    "pm25_pollution": "PM2.5 air pollution (µg/m³)",
    "log_pop_density": "Population density (people per km²)",
    "forest_ratio": "Forest coverage (% of land area)",
    "median_age": "Median age (years)",
    "secondary_edu_years": "Secondary education (years)",
    "life_expectancy": "Life expectancy (years)",
    "unemployment_rate": "Unemployment rate (%)",
    "log_area_sq_km": "Total area (km²)"
}

# possible variables panel
panel_vars = {
    "log_gdp_capita": "GDP per capita (current $US)",
    "hdi": "Human Developement Index (HDI)",
    "urban_pop_perc": "Urban population (%)",
    "log_population": "Total population",
    "pm25_pollution": "PM2.5 air pollution (µg/m³)",
    "log_pop_density": "Population density (people per km²)",
    "forest_ratio": "Forest coverage (% of land area)",
    "median_age": "Median age (years)",
    "secondary_edu_years": "Secondary education (years)",
    "life_expectancy": "Life expectancy (years)",
    "unemployment_rate": "Unemployment rate (%)",
}

# controls just placeholder because i'm not sure
controls = {
    "population": "Total population",
    "urban_pop_perc": "Urban population (%)",
    "pop_density": "Population density (people per km²)",
    "median_age": "Median age (years)",
    "secondary_edu_years": "Secondary education (years)",
    "unemployment_rate": "Unemployment rate (%)",
    "gdp_capita": "GDP per capita (current $US)",
    "continent": "Continent"
}

# possible questions (start with 5 for each model)
cross_questions = {
    "Is distance from the equator associated with HDI?": {"y": "hdi", "x": "distance_equator"},
    "Is urbanization associated with more GDP per capita?": {"y": "log_gdp_capita", "x": "urban_pop_perc"},
    "Is air pollution associated with life expectancy?": {"y": "life_expectancy", "x": "pm25_pollution"},
    "Is land area associated with GDP per capita?": {"y": "log_gdp_capita", "x": "log_area_sq_km"},
    "Is distance from the equator associated with median age?": {"y": "median_age", "x": "distance_equator"}
}

panel_questions = {
    "Is urbanization associated with HDI over time?": {"y": "hdi", "x": "urban_pop_perc"},
    "Is GDP per capita associated with life expectancy over time?": {"y": "life_expectancy", "x": "log_gdp_capita"},
    "Is pollution associated with life expectancy over time?": {"y": "life_expectancy", "x": "pm25_pollution"},
    "Is population density associated with unemployment over time?": {"y": "unemployment_rate", "x": "log_pop_density"},
    "Is urbanization associated with unemployment over time?": {"y": "unemployment_rate", "x": "urban_pop_perc"}
}

# title
with st.container(border=True):
    st.title("Regression models")
    st.write("change the paramenters of the regression model to learn more about the data")

# model choice (cross-country/panel)
model_choice = st.segmented_control("Regression model type", options=["Cross-sectional", "Panel"], default="Cross-sectional")
st.caption("Cross-sectional regression: examines the relationship between variables across countries at a single point in time")
st.caption("Panel regression: examines how a change within a country relates to an outcome over time")

# cross-country model
if model_choice == "Cross-sectional":
    with st.container(border=True):
        st.subheader("Cross-country regression")

        # choose a question
        question = st.selectbox("choose a question", options=list(cross_questions.keys()))

        # get x and y variable names 
        x_var = cross_questions[question]["x"]
        y_var = cross_questions[question]["y"]

        # choose a year with a slider
        year = st.slider("year", min_value=1990, max_value=2023, value=2020)

        # filter data for year
        model_data = df[df["year"] == year].copy()

        # keep only needed variables and drop missing observations (some countries have no observations in some years)
        model_data = model_data[[x_var, y_var]].dropna()

        # run regression (for now display the formula)
        formula = f"{y_var} ~ {x_var}"

        # standard error choice
        sd_choice = st.radio("Choose a standard error method:", ["Classical", "Robust (HC1)"])
        if sd_choice == "Classical":
            model = smf.ols(formula=formula, data=model_data).fit()

        else:
            model = smf.ols(formula=formula, data=model_data).fit(cov_type="HC1")

        # display regression results
        coef = model.params[x_var]
        se = model.bse[x_var]
        p_value = model.pvalues[x_var]
        r_squared = model.rsquared
        obs = int(model.nobs)
    
        cols = st.columns(2)
        with cols[0].container(border=True):
            st.subheader("Model results")
            st.write(f"Formula: {formula}")
            st.write("**Observations:**", obs)
            st.write("**Coefficient:**", f"{coef:.3f}")
            st.write("**Standard error:**", f"{se:.3f}")
            if p_value < 0.001:
                st.write("**p-value:** < 0.001")
            else:
                st.write("**p-value:**", f"{p_value:.3f}")
            st.write("**R-squared:**", f"{r_squared:.3f}")

        with cols[1].container(border=True):
            st.subheader("Interpretation:")
            st.write("written interpretation placeholder")
        
    with st.expander("show full regression output"):
        st.write(model.summary())





        
