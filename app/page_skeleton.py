# main file of app, global settings, builds menu, no content

# streamlit run app/page_skeleton.py     # start the app
# https://worldwise.streamlit.app


# import streamlit
import streamlit as st

# settings for the page
st.set_page_config(
    page_title="World Wise",  # text shown in the browser tab
    page_icon="🌍",  # icon shown in the browser tab
    layout="wide",  # full screen width
)


from pages import (home, game, main_plot, line_plot, models, world_map)

# sidebar menu
navigation = st.navigation(
    {  # dictionary: heading in the menu -> list of pages under that heading
        "Start": [home],  # heading "Start" with the home page
        # both analysis subpages grouped together for now
        "Data analysis": [main_plot, line_plot, models],
        "Explore": [world_map, game],  # the map
    }
)

navigation.run()  # show the page the user clicked (or the default page)
