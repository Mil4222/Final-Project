import streamlit as st
from pathlib import Path
import base64

# ideas for the homepage:
# - use png map as background (maybe not if it's too busy) (use CSS background image maybe)
# - use png logo at the top (use normal streamlit image)
# - under the logo we can add one "slogan"/description of the app (one sentence)
# - quick navigation to other pages (use st.page_link)
# - informations section but hidden (something like "about", "team", "sources",...)

# set path
project_root = Path(__file__).resolve().parents[1]
logo_path = project_root / "images" / "logo_image.png"
map_path = project_root / "images" / "map_image.png"

# logo 
st.image(logo_path, width="stretch")

# get links to all pages
from pages import (game, main_plot, line_plot, models, world_map)

# map background -> convert it to base 64
def get_base64_image(path):
    image_bytes = path.read_bytes()
    return base64.b64encode(image_bytes).decode()

map_base64 = get_base64_image(map_path)

# add background with css (add blur so it's not super distracting)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(
                rgba(255, 255, 255, 0.20),
                rgba(255, 255, 255, 0.20)
            ),
            url("data:image/png;base64,{map_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

with st.container(border=True):

    # here goes the subtitle
    st.subheader("**subtitle**")

    # page links 
    # so for the links I think I have to change the links 
    # I have to link to the st.page in skeleton -> create a new page just for the links
    cols = st.columns(5)
    with cols[0]:
        st.page_link(main_plot, label="scatter plot")
    with cols[1]:
        st.page_link(line_plot, label="line plot")
    with cols[2]:
        st.page_link(models, label="regression")
    with cols[3]:
        st.page_link(world_map, label="map")
    with cols[4]:
        st.page_link(game, label="game")

    # infos (hidden)
    with st.expander("about worldwise"):
        st.write("placeholder -> explain what is the app")
    with st.expander("about the team"):
        st.write("placeholder -> not super necessary but fun :)")
    with st.expander("data and sources"):
        st.write("placeholder")


