import pandas as pd
import streamlit as st
import statsmodels.formula.api as smf
from pathlib import Path
import numpy as np

# run page: streamlit run "app/regression.py"

# idea: since some variables have no within country change over the years (area, distance form equator,..)
# make two separate models: 
# - cross-sectional: compares countries in one selected year -> choose controls, SE (classic, robust) and year, maybe continent
# - panel: analyze changes within countries across years -> choose controls, SE (classic, robust, clustered by country), FE (year, country)
# For now i would just allow preset questions, not complete freedom for the user
# still allow some freedom with control choices and Se methods
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

# i need normal names for the interpretation card
interpret_names = {
    "hdi": "HDI",
    "distance_equator": "distance from the equator",
    "urban_pop_perc": "urban population share",
    "pm25_pollution": "PM2.5 pollution",
    "life_expectancy": "life expectancy",
    "median_age": "median age",
    "log_gdp_capita": "GDP per capita",
    "log_area_sq_km": "land area",
    "log_pop_density": "population density",
    "unemployment_rate": "unemployment rate"
}

# i also need normal units names for the interpretation
units = {
    "distance_equator": "degree",
    "urban_pop_perc": "percentage point",
    "pm25_pollution": "µg/m³",
    "life_expectancy": "year",
    "median_age": "year",
    "unemployment_rate": "percentage point"
}

# possible questions (start with 5 for each model) 
# i decided to add specific controls for each question (now just placeholder)
# cross: use more geo variables that don't change over time 
cross_questions = {
    "Is distance from the equator associated with HDI?": {"y": "hdi", "x": "distance_equator", "controls": ["log_population", "log_area_sq_km"]},
    # keep: connects geography with developement. controls: compare countries with similar size and pop -> continent FE?
    "Is urbanization associated with more GDP per capita?": {"y": "log_gdp_capita", "x": "urban_pop_perc", "controls": [["distance_equator", "log_population", "log_area_sq_km"]]},
    # keep: intuitive, important for developement. controls: compare countries with similar size and pop
    "Is air pollution associated with life expectancy?": {"y": "life_expectancy", "x": "pm25_pollution", "controls": ["log_gdp_capita", "urban_pop_perc", "forest_ratio"]},
    # Keep: intuitive, interesting, BUT super relevant for geo-socio, but only health. controls: important to control for how rich/urban a country is
    "Is population density related to GDP per capita?": {"y": "log_gdp_capita", "x": "log_pop_density", "controls": ["distance_equator", "urban_pop_perc", "log_population"]},
    # keep: geo-socio focused
    "Is distance from the equator associated with median age?": {"y": "median_age", "x": "distance_equator", "controls": ["log_gdp_capita", "urban_pop_perc", "log_population"]}
    # keep: strong association. controls: pop and area and gdp -> does this strong correlation perisists among similar incomes?
}

panel_questions = {
    "Is urbanization associated with HDI over time?": {"y": "hdi", "x": "urban_pop_perc", "controls": ["pm25_pollution", "log_population", "median_age"]},
    # keep: both change over time within a country and it's interesting. controls: do not use gdp!
    "Is GDP per capita associated with life expectancy over time?": {"y": "life_expectancy", "x": "log_gdp_capita", "controls": ["urban_pop_perc", "pm25_pollution"]},
    # idk: need constant gdp per capita
    "Is pollution associated with life expectancy over time?": {"y": "life_expectancy", "x": "pm25_pollution","controls": ["urban_pop_perc", "log_population"]},
    # keep: nice to have the same question in both models
    "Is urbanization associated with GDP per capita over time?": {"y": "log_gdp_capita", "x": "urban_pop_perc", "controls": ["log_gdp_capita", "urban_pop_perc"]},
    # idk: need the constant gdp per capita
    "Is forest coverage associated with air pollution over time?": {"y": "pm25_pollution", "x": "forest_coverage"}, 
    # maybe use this 
    "Is urbanization associated with unemployment over time?": {"y": "unemployment_rate", "x": "urban_pop_perc", "controls": ["log_gdp_capita", "log_pop_density"]}
}

# title
with st.container(border=True):
    st.title("Regression models")
    st.write("Change the paramenters of the regression model to learn more about the data")

# model choice (cross-country/panel)
model_choice = st.segmented_control(
    "Regression model type", 
    options=["Cross-sectional", "Panel"], 
    default="Cross-sectional",
    help="""
**Cross-sectional regression:** compares different countries at one point in time to see how two or more variables are related across countries

**Panel regression:** uses observations of the same countries across multiple years to study how variables are related over time
""")

# cross-country model
if model_choice == "Cross-sectional":
    with st.container(border=True):
        st.subheader("Cross-country regression")

        cols = st.columns(2)
        with cols[0]:
            # choose a question
            question = st.selectbox("Choose a question", options=list(cross_questions.keys()))
            # get x and y variable names 
            x_var = cross_questions[question]["x"]
            y_var = cross_questions[question]["y"]

        with cols[1]:
            # choose a year with a slider
            year = st.slider("Choose a year", min_value=1990, max_value=2023, value=2020)
            # filter data for year
            model_data = df[df["year"] == year].copy()  

        cols = st.columns(2)
        with cols[0]:
            # select question for controls and then display with multiselect
            question_info = cross_questions[question]
            x_var = question_info["x"]
            y_var = question_info["y"]
            available_controls = question_info["controls"]
            selected_controls = st.multiselect("Add controls", options=available_controls, format_func=lambda x: cross_vars[x], default=[])

            # keep only needed variables and drop missing observations (some countries have no observations in some years)
            needed_vars = [y_var, x_var] + selected_controls + ["country", "year"]
            model_data = model_data[needed_vars].dropna().copy()

            # formula (display for now) -> change it to add controls
            formula = f"{y_var} ~ {x_var}"
            if selected_controls:
                formula += " + " + " + ".join(selected_controls)

        with cols[1]:
            # standard error choice and run regression
            se_choice = st.radio(
                "Choose standard error method", 
                ["Classical", "Robust (HC1)"],
                help="""
            **Classical:** Assumes constant error variance and independent errors.

            **Robust (HC1):** Allows the error variance to differ across observations.
            """)
            if se_choice == "Classical":
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
            x_name = interpret_names[x_var]
            y_name = interpret_names[y_var]
            x_unit = units.get(x_var, "unit")
            controls_text = ("no additional controls" if len(selected_controls) == 0 else f"{len(selected_controls)} additional control(s)")
            x_logged = x_var.startswith("log_")
            y_logged = y_var.startswith("log_")

            st.subheader("Interpretation:")
        
            st.write("**Specification:**", f"cross-sectional OLS for {year} with {controls_text} and {se_choice.lower()} standard errors")

            if coef > 0:
                st.write("**Direction:** positive association")
            elif coef < 0:
                st.write("**Direction:** negative association")
            else:
                st.write("**Direction:** no association")

            if not x_logged and not y_logged:
                if coef > 0:
                    st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {coef:.3f} increase in {y_name}")
                elif coef < 0:
                    st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {coef:.3f} decrease in {y_name}")
                else: 
                    st.write("**Magnitude:** no association")

            elif not x_logged and y_logged:
                if coef > 0:
                    st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {100 * coef:.3f}% increase in {y_name}")
                elif coef < 0:
                    st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {100 * coef:.3f}% decrease in {y_name}")
                else: 
                    st.write("**Magnitude:** no association")

            elif x_logged and not y_logged:
                if coef > 0:
                    st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef/100:.3f} increase in {y_name}")
                elif coef < 0:
                    st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef/100:.3f} decrease in {y_name}")
                else: 
                    st.write("**Magnitude:** no association")

            else: # log-log
                if coef > 0:
                    st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef:.3f}% increase in {y_name}")
                elif coef < 0:
                    st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef:.3f}% decrease in {y_name}")
                else: 
                    st.write("**Magnitude:** no association")

            if p_value < 0.001:
                st.write("**Significance:** p < 0.001, the association is highly statistically significant")
            elif p_value < 0.01:
                st.write("**Significance:**", f"p < {p_value:.3f}, the association is statistically significant at the 1% level")
            elif p_value < 0.05:
                st.write("**Significance:**", f"p < {p_value:.3f}, the association is statistically significant at the 5% level")
            else: 
                st.write("**Significance:** the association is not statistically significant at the conventional levels")
        
        st.info("These coefficients are to be interpreted as associations, not causal relationships")

        
    with st.expander("Show full regression output"):
        st.write(model.summary())

# panel regression
else:
    with st.container(border=True):
        st.subheader("Panel regression")
    
        cols = st.columns(2)
        with cols[0]:
            # choose a question
            question = st.selectbox("Choose a question", options=list(panel_questions.keys()))
            # get x and y variable names 
            x_var = panel_questions[question]["x"]
            y_var = panel_questions[question]["y"]

        with cols[1]:
            # select question for controls and then display with multiselect
            question_info = panel_questions[question]
            x_var = question_info["x"]
            y_var = question_info["y"]
            available_controls = question_info["controls"]
            selected_controls = st.multiselect("Add controls", options=available_controls, format_func=lambda x: panel_vars[x], default=[])

            # keep variables for regression data and remove missing 
            needed_vars = [y_var, x_var] + selected_controls + ["country", "year"]
            model_data = df[needed_vars].dropna().copy()

        cols = st.columns(2)
        with cols[0]:
            # choose fixed effects and add explanations for FE
            fe_choice = st.radio(
                "Choose fixed effects", 
                ["Pooled OLS", "Country FE", "Year FE", "Country + Year FE"],
                help="""
            **Pooled OLS:** Uses all country-year observations without controlling for country-specific or year-specific effects.

            **Country fixed effects:** Controls for characteristics of each country that do not change over time. The coefficient is identified from changes within the same country.
            
            **Year FE:** Controls for shocks or trends that affect all countries in the same year.
            
            **Country + Year FE:** Controls for both time-invariant country characteristics and common year-specific shocks.
            """)

            # formula (display for now) -> change it to add controls and to add fixed effects
            formula = f"{y_var} ~ {x_var}"
            if selected_controls:
                formula += " + " + " + ".join(selected_controls)
            if fe_choice == "Country FE":
                formula += " + C(country)"
            elif fe_choice == "Year FE":
                formula += " + C(year)"
            elif fe_choice == "Country + Year FE":
                formula += " + C(country) + C(year)"
            # when we add controls observations can change a lot so I should display a message

        with cols[1]:
            # standard error choice and run regression and explanations
            se_choice = st.radio(
                "Choose standard error method", 
                ["Classical", "Robust (HC1)", "Clustered by country"],
                help="""
            **Classical:** Assumes constant error variance and independent errors.
            
            **Robust (HC1):** Allows the error variance to differ across observations.
            
            **Clustered by country:** Allows errors to be correlated within the same country over time. Best for panel data.
            """)
            if se_choice == "Classical":
                model = smf.ols(formula=formula, data=model_data).fit()
            elif se_choice == "Robust (HC1)":
                model = smf.ols(formula=formula, data=model_data).fit(cov_type="HC1")
            else:
                model = smf.ols(formula=formula, data=model_data).fit(cov_type="cluster", cov_kwds={"groups": model_data["country"]})

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
                x_name = interpret_names[x_var]
                y_name = interpret_names[y_var]
                x_unit = units.get(x_var, "unit")
                controls_text = ("no additional controls" if len(selected_controls) == 0 else f"{len(selected_controls)} additional control(s)")
                if fe_choice == "Year FE":
                    fe_text = "with year fixed effects"
                elif fe_choice == "Country FE":
                    fe_text = "with country fixed effects"
                elif fe_choice == "Country + Year FE":
                    fe_text = "with year and country fixed effects"
                else:
                    fe_text = ""
                x_logged = x_var.startswith("log_")
                y_logged = y_var.startswith("log_")

                st.subheader("Interpretation:")

                st.write("**Specification:**", f"panel OLS {fe_text}, {controls_text} and {se_choice.lower()} standard errors")
                
                if coef > 0:
                    st.write("**Direction:** positive association")
                elif coef < 0:
                    st.write("**Direction:** negative association")
                else:
                    st.write("**Direction:** no association")
                
                if not x_logged and not y_logged:
                    if coef > 0:
                        st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {coef:.3f} increase in {y_name}")
                    elif coef < 0:
                        st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {coef:.3f} decrease in {y_name}")
                    else: 
                        st.write("**Magnitude:** no association")
                
                elif not x_logged and y_logged:
                    if coef > 0:
                        st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {100 * coef:.3f}% increase in {y_name}")
                    elif coef < 0:
                        st.write("**Magnitude:**", f"a 1 {x_unit} increase in {x_name} is associated with a {100 * coef:.3f}% decrease in {y_name}")
                    else: 
                        st.write("**Magnitude:** no association")
                
                elif x_logged and not y_logged:
                    if coef > 0:
                        st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef/100:.3f} increase in {y_name}")
                    elif coef < 0:
                        st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef/100:.3f} decrease in {y_name}")
                    else: 
                        st.write("**Magnitude:** no association")
                
                else: # log-log
                    if coef > 0:
                        st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef:.3f}% increase in {y_name}")
                    elif coef < 0:
                        st.write("**Magnitude:**", f"a 1 % increase in {x_name} is associated with a {coef:.3f}% decrease in {y_name}")
                    else: 
                        st.write("**Magnitude:** no association")
                
                if p_value < 0.001:
                    st.write("**Significance:** p < 0.001, the association is highly statistically significant")
                elif p_value < 0.01:
                    st.write("**Significance:**", f"p < {p_value:.3f}, the association is statistically significant at the 1% level")
                elif p_value < 0.05:
                    st.write("**Significance:**", f"p < {p_value:.3f}, the association is statistically significant at the 5% level")
                else: 
                    st.write("**Significance:** the association is not statistically significant at the conventional levels")

        st.info("These coefficients are to be interpreted as associations, not causal relationships")
                
    with st.expander("Show full regression output"):
        st.write(model.summary())
    


# stuff to add next:
# - writte interpretation card 
# - polish the questions and the controls because now they are a little random (not 100% random tho)
# - change style and layout (but this for every page)
# - add explanations for the models (like what are "Year FE"?) to make it more educational -> maybe like a popup



        
