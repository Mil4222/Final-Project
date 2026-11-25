import pandas as pd
import streamlit as st
from pathlib import Path

# run game: streamlit run "app/guess_game.py"
# Import data 
project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "data_clean_final" / "final_clean.csv"

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, keep_default_na=False, na_values=[""])
    return df

df = load_data(data_path)

# create hemisphere variable (north True, south false)
df["hemi"] = df["capital_latitude"] >= 0
df["hemi"] = df["hemi"].replace({True: "Northern", False: "Southern"})
# actual continent names
df["continent"] =df["continent"].str.replace({"NA": "North America", "SA": "South America", "OC": "Oceania", "EU": "Europe", "AS": "Asia", "AF": "Africa"})

# I have to change because we are doing 2 modes: normal mode, hard mode
normal_vars = ["country", "continent", "population", "constant_gdp_capita", "area_sq_km", "capital_latitude", "capital_longitude"]
normal_game = (df[df["year"] == 2023][normal_vars].dropna().copy())

hard_vars = ["country", "continent", "hdi", "pm2.5_pollution", "pop_density", "urban_pop_perc"]
hard_game = (df[df["year"] == 2023][hard_vars].dropna().copy())

st.set_page_config(layout="wide")

# style for title (don't like it)
st.markdown(
    """
   <style>
    .st-key-title_card {
        background-color: #FFFDF7;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# style for guess container
st.markdown(
    """
    <style>
    .st-key-guess_card {
        background-color: #FFFDF7;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# style for history card
st.markdown(
    """
    <style>
    .st-key-history_card {
        background-color: #FFFDF7;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# add container/box for the title and instructions
with st.container(border=False, width="stretch"):
    st.title("Guess the Country")
    st.write("guess the mystery country using the clues")

# important: use st.session_state when something needs to be remembered during the full gamerun

# move reset button to the top beside game mode selection
mode_col, reset_col = st.columns([5, 1])

# choose game mode
with mode_col:
    mode = st.segmented_control("Game mode", options=["Normal", "Hard"], default="Normal")

# reset button (pick another random country)
with reset_col:
    st.write("")
    st.write("")
    reset_clicked = st.button("Reset Game", help="resetting the game will choose another random target country")
    
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

# win condition
if "guessed_correctly" not in st.session_state: 
    st.session_state.guessed_correctly = False

# text selectbox (changes after the first atempt)
if st.session_state.attempts == 0:
    placeholder_text = "start typing a country"
else: 
    placeholder_text = "start typing another country"

# text for the guess button (changes after the first attempt)
if st.session_state.attempts == 0:
    button_text = "Guess"
else:
    button_text = "Guess again"

# start game 
if not st.session_state.guessed_correctly:

    # add container for the input (man I should I have done this beforee :/)
    with st.container(border=True, width="stretch", key="guess_card"):
        st.subheader("make a guess!")

        # search bar
        country_list = sorted(game_data["country"].unique())
        user_guess = st.selectbox("enter a country", options=country_list, index=None, placeholder=placeholder_text)

        # guess button, then match searched country with country in the data
        if st.button(button_text):

            if user_guess is not None:
                guess = game_data[game_data["country"] == user_guess].iloc[0]
                st.session_state.attempts += 1

                # compare normal mode
                if mode == "Normal":

                    # compare emispehere --> normal mode still too difficult
                    # if guess["hemi"] == st.session_state.target["hemi"]:
                        # hemi_result = "correct"
                    # else:
                       #  hemi_result = "wrong"
                    
                    # compare continent -> use continent instead
                    if guess["continent"] == st.session_state.target["continent"]:
                        continent_result = "correct"
                    else:
                        continent_result = "wrong"

                    # Compare area (in square kilometers) -> 5% tolerance for correct
                    difference = abs(guess["area_sq_km"] - st.session_state.target["area_sq_km"])
                    tolerance = st.session_state.target["area_sq_km"] * 0.05
                    # try to add also "close" results
                    close_tolerance = st.session_state.target["area_sq_km"] * 0.10
                    if difference <= tolerance:
                        area_result = "correct"
                    elif difference <= close_tolerance:
                        area_result = "close"
                    elif guess["area_sq_km"] < st.session_state.target["area_sq_km"]:
                        area_result = "higher"
                    else:
                        area_result = "lower"

                    # Compare GDP per capita -> 5% tolerance for correct
                    difference = abs(guess["constant_gdp_capita"] - st.session_state.target["constant_gdp_capita"])
                    tolerance = st.session_state.target["constant_gdp_capita"] * 0.05
                    close_tolerance = st.session_state.target["constant_gdp_capita"] * 0.10
                    if difference <= tolerance:
                        gdp_result = "correct"
                    elif difference <= close_tolerance:
                        gdp_result = "close"
                    elif guess["constant_gdp_capita"] < st.session_state.target["constant_gdp_capita"]:
                        gdp_result = "higher"
                    else:
                        gdp_result = "lower"

                    # Compare population -> 5% tolerance
                    difference = abs(guess["population"] - st.session_state.target["population"])
                    tolerance = st.session_state.target["population"] * 0.05
                    close_tolerance = st.session_state.target["population"] * 0.10
                    if difference <= tolerance:
                        pop_result = "correct"
                    elif difference <= close_tolerance:
                        pop_result = "close"
                    elif guess["population"] < st.session_state.target["population"]:
                        pop_result = "higher"
                    else:
                        pop_result = "lower"

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

                    # game history table (normal mode)-> also display value
                    st.session_state.history.append({
                        "Attempt": st.session_state.attempts,
                        "Country": guess["country"],
                        "Continent": {
                            "value": guess["continent"],
                            "result": continent_result
                        },
                        "Area": {
                            "value": guess["area_sq_km"],
                            "result": area_result
                        },
                        "Population": {
                            "value": guess["population"],
                            "result": pop_result
                        },
                        "GDP per capita": {
                            "value": guess["constant_gdp_capita"],
                            "result": gdp_result
                        },
                        "Direction": direction
                    })

                # comparisons for hard mode
                else:

                    # compare continent 
                    if guess["continent"] == st.session_state.target["continent"]:
                        continent_result = "correct"
                    else:
                        continent_result = "wrong"

                    # compare population density -> 5% tolerance
                    difference = abs(guess["pop_density"] - st.session_state.target["pop_density"]) 
                    tolerance = st.session_state.target["pop_density"] * 0.05
                    close_tolerance = st.session_state.target["pop_density"] * 0.10
                    if difference <= tolerance:
                        density_result = "correct"
                    elif difference <= close_tolerance:
                        density_result = "close"
                    elif guess["pop_density"] < st.session_state.target["pop_density"]:
                        density_result = "higher"
                    else:
                        density_result = "lower"

                    # Compare hdi -> 5% tolerance
                    difference = abs(guess["hdi"] - st.session_state.target["hdi"])
                    tolerance = st.session_state.target["hdi"] * 0.05
                    close_tolerance = st.session_state.target["hdi"] * 0.10
                    if difference <= tolerance:
                        hdi_result = "correct"
                    elif difference <= close_tolerance:
                        hdi_result = "close"
                    elif guess["hdi"] < st.session_state.target["hdi"]:
                        hdi_result = "higher"
                    else:
                        hdi_result = "lower"

                    # Compare pollution -> 5% tolerance
                    difference = abs(guess["pm2.5_pollution"] - st.session_state.target["pm2.5_pollution"]) 
                    tolerance = st.session_state.target["pm2.5_pollution"] * 0.05 
                    close_tolerance = st.session_state.target["pm2.5_pollution"] * 0.10
                    if difference <= tolerance:
                        pollution_result = "correct"
                    elif difference <= close_tolerance:
                        pollution_result = "close"
                    elif guess["pm2.5_pollution"] < st.session_state.target["pm2.5_pollution"]:
                        pollution_result = "higher"
                    else:
                        pollution_result = "lower"

                    # compare urban population (as % of total population)
                    difference = abs(guess["urban_pop_perc"] - st.session_state.target["urban_pop_perc"]) 
                    tolerance = 2 # percentage points for tolerance
                    close_tolerance = 4
                    if difference <= tolerance:
                        urban_result = "correct"
                    elif difference <= close_tolerance:
                        urban_result = "close"
                    elif guess["urban_pop_perc"] < st.session_state.target["urban_pop_perc"]:
                        urban_result = "higher"
                    else:
                        urban_result = "lower"

                    # game history table (hard mode)
                    st.session_state.history.append({
                        "Attempt": st.session_state.attempts,
                        "Country": guess["country"],
                        "Continent": {
                            "value": guess["continent"],
                            "result": continent_result
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
                        "HDI": {
                            "value": guess["hdi"],
                            "result": hdi_result
                        }
                     })
    
                # win condition 
                if guess["country"] == st.session_state.target["country"]:
                    st.success(f"you win in {st.session_state.attempts} guesses!")
                    st.session_state.guessed_correctly = True
                else:
                    st.info("Wrong! Choose another country above and press **Guess again**.")

# display game history table (only after each guess) -> problem: the game should not look like this

# use html to color each card
def result_card(value, result):
    if result == "correct":
        background = "#bbedb6"
    elif result in ["wrong", "higher", "lower"]:
        background = "#f7a49c"
    else:
        background = "#fcee9f"

    st.markdown(
        f"""
        <div style="
            background-color: {background};
            color: #222222;
            padding: 15px;
            border-radius: 10px;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
            box-sizing: border-box;
        ">
            <strong>{value}</strong>
            <br>
            {result}
        </div>
        """,
        unsafe_allow_html=True
    )


# now i will use the game history to create the UI -> use st.columns to create one row for each guess
# add also column headers
# add container for the game history/clues

if st.session_state.history:

    with st.container(border=True, width="stretch", key="history_card"):

        if mode == "Normal":

            # headers (normal mode) -> use html to center the text
            headers_normal = ["Country", "Continent", "Area", "Population", "GDP per capita", "Direction"]
            header_cols = st.columns(6)
            for col, header in zip(header_cols, headers_normal):
                col.markdown(f"<div style='text-align: center;'><strong>{header}</strong></div>", unsafe_allow_html=True)

            # rows -> add container for each clue
            for row in st.session_state.history:
                cols = st.columns([1.40, 1.40, 1.40, 1.40, 1.40, 1.40], gap="medium")

                with cols[0].container(border=True):
                    st.write(row["Country"])
                with cols[1]:
                    result_card(row["Continent"]["value"], row["Continent"]["result"])
                with cols[2]:
                    result_card(f'{row["Area"]["value"]:,.0f} km²', row["Area"]["result"])
                with cols[3]:
                    result_card(f'{row["Population"]["value"]/1_000_000:.1f} M', row["Population"]["result"])
                with cols[4]:
                    result_card(f'${row["GDP per capita"]["value"]:,.0f}', row["GDP per capita"]["result"])
                with cols[5].container(border=True):
                    st.write(row["Direction"])

                st.space("xsmall") # space between cards (vertically)
                
        else:

            # headers (hard mode) -> use html to center the text
            headers_hard = ["Country", "Continent", "Population density", "PM2.5 pollution", "Urban population", "HDI"]
            header_cols = st.columns(6)
            for col, header in zip(header_cols, headers_hard):
                col.markdown(f"<div style='text-align: center;'><strong>{header}</strong></div>", unsafe_allow_html=True)
        
            # rows -> add container for each clue
            for row in st.session_state.history:
                cols = st.columns([1.40, 1.40, 1.40, 1.40, 1.40, 1.40], gap="medium")
        
                with cols[0].container(border=True):
                    st.write(row["Country"])
                with cols[1]:
                    result_card(row["Continent"]["value"], row["Continent"]["result"])
                with cols[2]:
                    result_card(f'{row["Population density"]["value"]:,.1f}/km²', row["Population density"]["result"])
                with cols[3]:
                    result_card(f'{row["PM2.5 pollution"]["value"]:.1f} PM2.5 (µg/m³)', row["PM2.5 pollution"]["result"])
                with cols[4]:
                    result_card(f'{row["Urban population"]["value"]:.1f}%', row["Urban population"]["result"])
                with cols[5]:
                    result_card(f'{row["HDI"]["value"]:.3f}', row["HDI"]["result"])

                st.space("xsmall")
        
# reset button 
if reset_clicked:
    st.session_state.target = game_data.sample(1).iloc[0]
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.guessed_correctly = False
    st.rerun()


