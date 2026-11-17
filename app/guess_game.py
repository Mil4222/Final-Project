import pandas as pd
import streamlit as st
from pathlib import Path

# Import data -> NOT FINAL DATA, JUST PLACEHOLDER!
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "data_clean_final" / "final_clean.csv"
df = pd.read_csv(data_path, keep_default_na=False, na_values=[""])

# I have to change because we are doing 2 modes: normal mode, hard mode
normal_vars = ["country", "continent", "population", "gdp_capita", "area_sq_km", "hdi"]
normal_game = (df[df["year"] == 2023][normal_vars].dropna().copy())

hard_vars = ["country", "capital_latitude", "capital_longitude", "median_age", "pm2.5_pollution", "pop_density", "urban_pop_perc"]
hard_game = (df[df["year"] == 2023][hard_vars].dropna().copy())

# add container/box for the title and instructions
with st.container(border=True):
    st.title("Guess the Country")
    st.write("guess the mystery country using the clues")

# important: use st.session_state when something needs to be remembered during the full gamerun

# choose game mode
mode = st.segmented_control("Game mode", options=["Normal", "Hard"], default="Normal")

# choose which data frame to use 
if mode == "Normal":
    game_data = normal_game
else:
    game_data = hard_game

# rember which mode we are in currently 
if "game_mode" not in st.session_state:
    st.session_state.game_mode = mode

# if the user changes mode mid game, the game resets
if st.session_state.game_mode != mode:
    st.session_state.game_mode = mode
    st.session_state.target = game_data.sample(1).iloc[0]
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.guessed_correctly = False
    st.rerun()

# pick a random country from the list (only once)
if "target" not in st.session_state:
    st.session_state.target = game_data.sample(1).iloc[0]

# st.write("target:", st.session_state.target["country"])

# attempts
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

# game history
if "history" not in st.session_state:
    st.session_state.history = []

if "guessed_correctly" not in st.session_state: 
    st.session_state.guessed_correctly = False

# start game 
if not st.session_state.guessed_correctly:

    # add container for the input (man I should I have done this beforee :/)
    with st.container(border=True):
        st.subheader("make a guess!")

        # search bar
        country_list = sorted(game_data["country"].unique())
        user_guess = st.selectbox("enter a country", options=country_list, index=None, placeholder="start typing a country")

        # guess button, then match searched country with country in the data
        if st.button("guess"):

            if user_guess is not None:
                guess = game_data[game_data["country"] == user_guess].iloc[0]
                st.session_state.attempts += 1

                # compare normal mode
                if mode == "Normal":

                    # compare continent 
                    if guess["continent"] == st.session_state.target["continent"]:
                        continent_result = "correct"
                    else:
                        continent_result = "wrong"

                    # Compare area (in square kilometers) -> 10% tolerance
                    difference = abs(guess["area_sq_km"] - st.session_state.target["area_sq_km"])
                    tolerance = st.session_state.target["area_sq_km"] * 0.10
                    if difference <= tolerance:
                        area_result = "correct"
                    elif guess["area_sq_km"] < st.session_state.target["area_sq_km"]:
                        area_result = "higher"
                    else:
                        area_result = "lower"

                    # Compare GDP per capita -> 10% tolerance
                    difference = abs(guess["gdp_capita"] - st.session_state.target["gdp_capita"])
                    tolerance = st.session_state.target["gdp_capita"] * 0.10
                    if difference <= tolerance:
                        gdp_result = "correct"
                    elif guess["gdp_capita"] < st.session_state.target["gdp_capita"]:
                        gdp_result = "higher"
                    else:
                        gdp_result = "lower"

                    # Compare population -> 10% tolerance
                    difference = abs(guess["population"] - st.session_state.target["population"])
                    tolerance = st.session_state.target["population"] * 0.10
                    if difference <= tolerance:
                        pop_result = "correct"
                    elif guess["population"] < st.session_state.target["population"]:
                        pop_result = "higher"
                    else:
                        pop_result = "lower"

                    # Compare hdi -> 10% tolerance
                    difference = abs(guess["hdi"] - st.session_state.target["hdi"])
                    tolerance = st.session_state.target["hdi"] * 0.10
                    if difference <= tolerance:
                        hdi_result = "correct"
                    elif guess["hdi"] < st.session_state.target["hdi"]:
                        hdi_result = "higher"
                    else:
                        hdi_result = "lower"

                    # game history table (normal mode)-> also display value
                    st.session_state.history.append({
                        "Attempt": st.session_state.attempts,
                        "Country": guess["country"],
                        "Continent": continent_result,
                        "Area": {
                            "value": guess["area_sq_km"],
                            "result": area_result
                        },
                        "Population": {
                            "value": guess["population"],
                            "result": pop_result
                        },
                        "GDP per capita": {
                            "value": guess["gdp_capita"],
                            "result": gdp_result
                        },
                        "HDI": {
                            "value": guess["hdi"],
                            "result": hdi_result
                        }
                    })

                # comparisons for hard mode
                else:

                    # compare population density -> 10% tolerance
                    difference = abs(guess["pop_density"] - st.session_state.target["pop_density"]) # take absolute value of the difference
                    tolerance = st.session_state.target["pop_density"] * 0.10 # 10% of the target value
                    if difference <= tolerance:
                        density_result = "correct"
                    elif guess["pop_density"] < st.session_state.target["pop_density"]:
                        density_result = "higher"
                    else:
                        density_result = "lower"

                    # Compare median age -> 10% tolerance
                    difference = abs(guess["median_age"] - st.session_state.target["median_age"]) # take absolute value of the difference
                    tolerance = st.session_state.target["median_age"] * 0.10 # 10% of the target value
                    if difference <= tolerance:
                        age_result = "correct"
                    elif guess["median_age"] < st.session_state.target["median_age"]:
                        age_result = "higher"
                    else:
                        age_result = "lower"

                    # Compare pollution -> 10% tolerance
                    difference = abs(guess["pm2.5_pollution"] - st.session_state.target["pm2.5_pollution"]) # take absolute value of the difference
                    tolerance = st.session_state.target["pm2.5_pollution"] * 0.10 # 10% of the target value
                    if difference <= tolerance:
                        pollution_result = "correct"
                    elif guess["pm2.5_pollution"] < st.session_state.target["pm2.5_pollution"]:
                        pollution_result = "higher"
                    else:
                        pollution_result = "lower"

                    # compare urban population (as % of total population)
                    difference = abs(guess["urban_pop_perc"] - st.session_state.target["urban_pop_perc"]) # take absolute value of the difference
                    tolerance = 3 # percentage points for tolerance
                    if difference <= tolerance:
                        urban_result = "correct"
                    elif guess["urban_pop_perc"] < st.session_state.target["urban_pop_perc"]:
                        urban_result = "higher"
                    else:
                        urban_result = "lower"

                    # compare latitude -> 3 tolerance 
                    lat_diff = st.session_state.target["capital_latitude"] - guess["capital_latitude"]
                    lon_diff = st.session_state.target["capital_longitude"] - guess["capital_longitude"]
                    tolerance = 3
    
                    if lat_diff > tolerance:
                        vertical = "north"
                    elif lat_diff < -tolerance:
                        vertical = "south"
                    else:
                        vertical = ""
    
                    # compare longitude
                    if lon_diff > tolerance:
                        horizontal = "east"
                    elif lon_diff < -tolerance:
                        horizontal = "west"
                    else:
                        horizontal = ""
    
                    # combine directions togheter
                    if vertical and horizontal:
                        direction = f"{vertical}-{horizontal}"
                    elif vertical:
                        direction = vertical
                    elif horizontal:
                        direction = horizontal
                    else:
                        direction = "correct"

                    # game history table (hard mode)
                    st.session_state.history.append({
                        "Attempt": st.session_state.attempts,
                        "Country": guess["country"],
                        "Median age": {
                            "value": guess["median_age"],
                            "result": age_result
                        },
                        "Population density": {
                            "value": guess["pop_density"],
                            "result": density_result
                        },
                        "PM2.5 pollution": {
                            "value": guess["pm2.5_pollution"],
                            "result": pollution_result
                        },
                        "Urban population": {
                            "value": guess["urban_pop_perc"],
                            "result": urban_result
                        },
                        "Direction": direction
                     })
    
                # win condition 
                if guess["country"] == st.session_state.target["country"]:
                    st.success(f"you win in {st.session_state.attempts} guesses!")
                    st.session_state.guessed_correctly = True
                else:
                    st.write("try again")

# display game history table (only after each guess) -> problem: the game should not look like this
# now i will use the game history to create the UI -> use st.columns to create one row for each guess
# add also column headers
# add container for the game history/clues

if st.session_state.history:

    with st.container(border=True):

        if mode == "Normal":

            # headers (normal mode)
            header_cols = st.columns(6)
            header_cols[0].markdown("**Country**")
            header_cols[1].markdown("**Continent**")
            header_cols[2].markdown("**Area**")
            header_cols[3].markdown("**Population**")
            header_cols[4].markdown("**GDP per capita**")
            header_cols[5].markdown("**HDI**")

            # rows -> add container for each clue
            for row in st.session_state.history:
                cols = st.columns([1.40, 1.15, 1.40, 1.30, 1.30, 1.30])

                with cols[0].container(border=True):
                    st.write(row["Country"])
                with cols[1].container(border=True):
                    st.write(row["Continent"])
                with cols[2].container(border=True):
                    st.write(f'{row["Area"]["value"]:.0f} km²\n{row["Area"]["result"]}')
                with cols[3].container(border=True):
                    st.write(f'{row["Population"]["value"]/1_000_000:.1f} M\n{row["Population"]["result"]}')
                with cols[4].container(border=True):
                    st.write(f'{row["GDP per capita"]["value"]:,.0f}$\n{row["GDP per capita"]["result"]}')
                with cols[5].container(border=True):
                    st.write(f'{row["HDI"]["value"]:.3f}\n{row["HDI"]["result"]}')

        else:
        
            # headers (hard mode)
            header_cols = st.columns(6)
            header_cols[0].markdown("**Country**")
            header_cols[1].markdown("**Median age**")
            header_cols[2].markdown("**Population density**")
            header_cols[3].markdown("**PM2.5 pollution**")
            header_cols[4].markdown("**Urban population**")
            header_cols[5].markdown("**Direction**")
        
            # rows -> add container for each clue
            for row in st.session_state.history:
                cols = st.columns([1.40, 1.30, 1.30, 1.30, 1.30, 1.15])
        
                with cols[0].container(border=True):
                    st.write(row["Country"])
                with cols[1].container(border=True):
                    st.write(f'{row["Median age"]["value"]:.1f} years\n{row["Median age"]["result"]}')
                with cols[2].container(border=True):
                    st.write(f'{row["Population density"]["value"]:,.1f}/km²\n{row["Population density"]["result"]}')
                with cols[3].container(border=True):
                    st.write(f'{row["PM2.5 pollution"]["value"]:.1f} PM2.5 (µg/m³)\n{row["PM2.5 pollution"]["result"]}')
                with cols[4].container(border=True):
                    st.write(f'{row["Urban population"]["value"]:.1f}%\n{row["Urban population"]["result"]}')
                with cols[5].container(border=True):
                    st.write(row["Direction"])
        


# reset button: pick another random country
if st.button("new game"):
    st.session_state.target = game_data.sample(1).iloc[0]
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.guessed_correctly = False
    st.rerun()

st.caption("starting a new game will choose another random target country")