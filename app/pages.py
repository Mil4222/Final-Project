
import streamlit as st

# just configuration for the pages
# because i need the same st.page obejcts both in the skeleton and in home 

home = st.Page("home.py", title="Home", icon=":material/home:",
               default=True)  # start page, opens first
game = st.Page("guess_game.py", title="Guess the Country",
               icon=":material/quiz:")  # the guessing game
main_plot = st.Page("analysis_main.py", title="Main plot",
                    icon=":material/scatter_plot:")  # analysis subpage 1
line_plot = st.Page("line_plot.py", title="Trends over time",
                    icon=":material/show_chart:")  # analysis subpage 2
world_map = st.Page("map.py", title="Interactive map",
                    icon=":material/public:")  # map page
models = st.Page("regression.py", title="Regression models",
                 icon=":material/sync_alt:")  # analysis subpage 3
