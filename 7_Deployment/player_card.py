"""
# Player Card App - Streamlit 
# Inspired by: https://docs.streamlit.io/get-started, https://www.youtube.com/playlist?list=PLJJOI_ZUeaBphhaFWf2fotnKhF95MdI4g
#Import Libraries
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="NFL Injury Player Card",
    page_icon=":football:",
    initial_sidebar_state="expanded",
)

##########################################
##  Load and Prep Data                  ##
##########################################


@st.cache_data
def load_data():
    nflplayer = pd.read_csv("../1_DataCollection/src/team_rosters.csv")
    nflplayer["age"] = pd.to_numeric(nflplayer["age"], errors="coerce")
    nflplayer["season"] = pd.to_numeric(nflplayer["season"], errors="coerce")

    return nflplayer


@st.cache_data
def load_injuries():
    nflinjury = pd.read_csv("../1_DataCollection/src/injuries.csv")

    nflinjury["season"] = pd.to_numeric(nflinjury["season"], errors="coerce")
    nflplayer["team"] = nflplayer["team"].astype(str)
    nflinjury["player"] = nflinjury["full_name"].astype(str)


##########################################
##  Style and Formatting                ##
##########################################


##########################################
##  Title, Tabs, and Sidebar            ##
##########################################


##########################################
## Player Tab                           ##
##########################################


# Function to show player information
def show_player_info():
    st.header("Player Information")
    col1, col2 = st.columns(
        2
    )  # Ref: https://www.youtube.com/watch?v=clFrWjiwxL0&list=PLJJOI_ZUeaBphhaFWf2fotnKhF95MdI4g&index=30
    with col1:
        st.image(
            "https://static01.nyt.com/images/2019/12/10/sports/10nfl-injuries-1/10nfl-injuries-1-superJumbo.jpg?quality=90&auto=webp"
        )

    nflplayer = load_data()
    player_names = nflplayer["player_name"].unique()
    teams = nflplayer["team"].unique()
    selected_team = st.selectbox("Select a team", teams)
    selected_player = st.selectbox("Select a player", player_names)
    player_info = nflplayer[nflplayer["player_name"] == selected_player]
    st.write(player_info)


##########################################
## Injury Section                       ##
##########################################


# Function to show injury prediction visualization
def show_injury_prediction():
    st.header("Injury Prediction Visualization")

    # Placeholder for injury prediction visualization
    st.write("Injury prediction model visualization will be displayed here.")


##########################################
## Season Section                       ##
##########################################


# Function to show season schedule
def show_season_schedule():
    st.header("Season Schedule")
    # Placeholder for season schedule
    st.write("Season schedule will be displayed here.")


##########################################
## Weather Stadium Section              ##
##########################################


# Function to show weather and stadium information
def show_weather_stadium_info():
    st.header("Weather and Stadium Information")
    # Placeholder for weather and stadium info
    st.write("Weather and stadium information will be displayed here.")


##########################################
## Injury Section                       ##
##########################################


# Function to show another injury indicator
def show_injury_indicator():
    st.header("Injury Indicator")
    # Placeholder for another injury indicator
    st.write("Another injury indicator will be displayed here.")


##########################################
## Injury Section                       ##
##########################################


# Main app
def main():
    st.title("NFL Injury Player Cards")

    page = st.sidebar.selectbox(
        "Choose a Page",
        ["Player Info and Prediction", "Season Schedule and Injury Indicator"],
    )

    if page == "Player Info and Prediction":
        show_player_info()
        show_injury_prediction()
    elif page == "Season Schedule and Injury Indicator":
        show_season_schedule()
        show_weather_stadium_info()
        show_injury_indicator()


if __name__ == "__main__":
    main()
