# main file of app, global settings, builds menu, no content

# streamlit run app/page_skeleton.py     # start the app

# import streamlit
import streamlit as st

# settings for the page
st.set_page_config(
    page_title="World Wise",  # text shown in the browser tab
    page_icon="🌍",  # icon shown in the browser tab
    layout="wide",  # full screen width
)


# layout draft
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

# sidebar menu
navigation = st.navigation(
    {  # dictionary: heading in the menu -> list of pages under that heading
        "Start": [home],  # heading "Start" with the home page
        # both analysis subpages grouped together for now
        "Data analysis": [main_plot, line_plot],
        "Explore": [world_map, game],  # the map
    }
)

navigation.run()  # show the page the user clicked (or the default page)
