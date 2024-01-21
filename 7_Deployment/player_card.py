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
    nflplayer = load_data()

    # Team and Player Selection
    teams = nflplayer["team"].unique()
    selected_team = st.selectbox("Select a team", teams)
    team_players = nflplayer[nflplayer["team"] == selected_team]
    player_names = team_players["player_name"].unique()
    selected_player = st.selectbox("Select a player", player_names)

    # Filtered Player Information
    player_info = team_players[team_players["player_name"] == selected_player]

    # 2x2 Grid Layout
    col1, col2, col3, col4 = st.columns(4)

    # Personal Information
    with col1:
        st.subheader("Personal Info")
        st.write(f"Name: {player_info['player_name'].iloc[0]}")
        st.write(f"Age: {player_info['age'].iloc[0]}")

    # Physical Attributes
    with col2:
        st.subheader("Physical Attributes")
        st.write(f"Height: {player_info['height'].iloc[0]}")
        st.write(f"Weight: {player_info['weight'].iloc[0]}")

    # Professional Details
    with col3:
        st.subheader("Professional Details")
        st.write(f"Team: {player_info['team'].iloc[0]}")
        st.write(f"Jersey Number: {player_info['jersey_number'].iloc[0]}")
        st.write(f"Status: {player_info['status'].iloc[0]}")

    # Additional Information
    with col4:
        st.subheader("Additional Info")
        st.write(f"College: {player_info['college'].iloc[0]}")
        st.write(f"Years Exp: {player_info['years_exp'].iloc[0]}")

    # Display player headshot in the sidebar if URL exists
    if not player_info["headshot_url"].empty:
        headshot_url = player_info["headshot_url"].iloc[0]
        if headshot_url:
            st.sidebar.image(headshot_url, caption=selected_player)


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
