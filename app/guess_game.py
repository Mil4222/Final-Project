import pandas as pd
import streamlit as st
from pathlib import Path

# Import data -> NOT FINAL DATA, JUST PLACEHOLDER!
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "clean_data_tea" / "geo_merged.csv"
df = pd.read_csv(data_path, keep_default_na=False)

# clean
df["forest_ratio"] = pd.to_numeric(df["forest_ratio"], errors="coerce")
df["pop_density"] = pd.to_numeric(df["pop_density"], errors="coerce")
df["area_sq_km"] = pd.to_numeric(df["area_sq_km"], errors="coerce")
df["capital_longitude"] = pd.to_numeric(df["capital_longitude"], errors="coerce")
df["capital_latitude"] = pd.to_numeric(df["capital_latitude"], errors="coerce")

# placeholder year
game_data = df[df["year"] == 2023].copy()

# drop missing (again palestine and israel no coordinates)
game_data.dropna(inplace=True)

# keep only some indicators -> NOT FINAL, PLACEHOLDER!
game_data = game_data[["country", "continent", "pop_density", "forest_ratio", "area_sq_km", "capital_longitude", "capital_latitude"]]

st.title("Guess the Country")
st.write("guess the mystery country using the clues")

# important: use st.session_state when something needs to be remembered during the full gamerun

# pick a random country from the list (only once)
if "target" not in st.session_state:
    st.session_state.target = game_data.sample(1).iloc[0]

st.write("target:", st.session_state.target["country"])

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

    # search bar
    country_list = sorted(game_data["country"].unique())
    user_guess = st.selectbox("enter a country", options=country_list, index=None, placeholder="start typing a country")

    # guess button, then match searched country with country in the data
    if st.button("guess"):

        if user_guess is not None:
            guess = game_data[game_data["country"] == user_guess].iloc[0]

            st.session_state.attempts += 1

            # compare continent 
            if guess["continent"] == st.session_state.target["continent"]:
                continent_result = "correct"
            else:
                continent_result = "wrong"

            st.write("continent:", continent_result)

            # compare population density -> 10% tolerance
            difference = abs(guess["pop_density"] - st.session_state.target["pop_density"]) # take absolute value of the difference
            tolerance = st.session_state.target["pop_density"] * 0.10 # 10% of the target value
    
            if difference <= tolerance:
                density_result = "correct"
            elif guess["pop_density"] < st.session_state.target["pop_density"]:
                density_result = "higher"
            else:
                density_result = "lower"
    
            st.write("population density:", density_result)

            # Compare forest coverage -> tolareance of 3 percentage points (for now)
            difference = abs(guess["forest_ratio"] - st.session_state.target["forest_ratio"]) 
            tolerance = 3 
    
            if difference <= tolerance:
                forest_result = "correct"
            elif guess ["forest_ratio"] < st.session_state.target["forest_ratio"]:
                forest_result = "higher"
            else:
                forest_result = "lower"
    
            st.write("forest coverage:", forest_result)

            # Compare area (in square kilometers) -> 10% tolerance
            difference = abs(guess["area_sq_km"] - st.session_state.target["area_sq_km"])
            tolerance = st.session_state.target["area_sq_km"] * 0.10
    
            if difference <= tolerance:
                area_result = "correct"
            elif guess["area_sq_km"] < st.session_state.target["area_sq_km"]:
                area_result = "higher"
            else:
                area_result = "lower"
    
            st.write("area:", area_result)

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
    
            st.write("direction:", direction)

            # game history table 
            st.session_state.history.append({
                "Attempt": st.session_state.attempts,
                "Country": guess["country"],
                "Continent": continent_result,
                "Population density": density_result,
                "Forest coverage": forest_result,
                "Area": area_result,
                "Direction": direction
             })
    
            # win condition 
            if guess["country"] == st.session_state.target["country"]:
                st.success(f"you win in {st.session_state.attempts} guesses!")
                st.session_state.guessed_correctly = True
            else:
                st.write("try again")

# display game history table 
history_df = pd.DataFrame(st.session_state.history)

st.write("\nGuess history:")
st.dataframe(history_df)

# reset button: pick another random country
if st.button("new game"):
    st.session_state.target = game_data.sample(1).iloc[0]
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.guessed_correctly = False
    st.rerun()

st.caption("starting a new game will choose another random target country")