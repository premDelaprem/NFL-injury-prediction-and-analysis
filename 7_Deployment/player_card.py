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
import time

st.set_page_config(
    page_title="2022 NFL Injury Player Card",
    page_icon=":football:",
    initial_sidebar_state="expanded",
)

##########################################
##  Load and Prep Data                  ##
##########################################


@st.cache_data
def load_data():
    nflplayer = pd.read_csv("../7_Deployment/src/team_rosters.csv")

    return nflplayer


@st.cache_data
def load_injuries():
    nflinjury = pd.read_csv("../7_Deployment/src/clean_merged_data.csv")
    nflinjury["full_name_lower"] = nflinjury["full_name"].str.lower()

    # Grouping and counting injuries
    injury_counts = (
        nflinjury.groupby(["full_name_lower", "injury_category"])
        .size()
        .reset_index(name="counts")
    )

    # Renaming columns but keeping 'full_name_lower' unchanged
    injury_counts = injury_counts.rename(
        columns={
            "full_name_lower": "Full Name Lower",
            "injury_category": "Injury Category",
            "counts": "Counts",
        }
    )

    return injury_counts


@st.cache_data
def load_predictions():
    predictions = pd.read_csv("../7_Deployment/src/results.csv")
    # Ensure that the player name is in the same format as used in player_info
    predictions["Player Name"] = predictions["Player Name"].str.lower()  # If needed
    return predictions


@st.cache_data
def load_schedule():
    schedule = pd.read_parquet("../data/games.parq")
    # Select only the required columns
    schedule = schedule[
        [
            "season",
            "week",
            "homeTeamAbbr",
            "visitorTeamAbbr",
            "homeFinalScore",
            "visitorFinalScore",
        ]
    ]
    # Rename columns to proper format
    schedule = schedule.rename(
        columns={
            "season": "Season",
            "week": "Week",
            "homeTeamAbbr": "Home Team",
            "visitorTeamAbbr": "Visitor Team",
            "homeFinalScore": "Home Final Score",
            "visitorFinalScore": "Visitor Final Score",
        }
    )

    # Convert 'Season' to string to avoid formatting with commas
    schedule["Season"] = schedule["Season"].astype(int).astype(str)

    return schedule


# @st.cache_data
# def load_weather():
#     inj_ind = pd.read_csv("../7_Deployment/src/inj_ind.csv")


##########################################
##  Style and Formatting                ##
##########################################


##########################################
##  Title, Tabs, and Sidebar            ##
##########################################


########################################################
##                      Player Tab                    ##
# REF: https://docs.streamlit.io/library/cheatsheet   ##
########################################################


# Function to show player information
def show_player_info():
    st.header("Player Information")
    nflplayer = load_data()

    # Sidebar for Team and Player Selection
    teams = nflplayer["team"].unique()
    default_team_index = teams.tolist().index("BAL") if "BAL" in teams else 0
    selected_team = st.sidebar.selectbox(
        "Select a team", teams, index=default_team_index
    )

    # Filter players based on selected team
    team_players = nflplayer[nflplayer["team"] == selected_team]

    # Player Selection with Lamar Jackson as default (if available)
    player_names = team_players["player_name"].unique()
    default_player_index = (
        player_names.tolist().index("Lamar Jackson")
        if "Lamar Jackson" in player_names
        else 0
    )
    selected_player = st.sidebar.selectbox(
        "Select a player", player_names, index=default_player_index
    )

    # Display selected player's information
    if selected_player:
        player_info = team_players[team_players["player_name"] == selected_player]
        player_info["player_name_lower"] = player_info["player_name"].str.lower()

    with st.spinner(text="In progress"):
        time.sleep(2)
        # st.success("Done")

    # 2x2 Grid Layout
    col1, col2, col3, col4 = st.columns(4)

    # Personal Information
    with col1:
        st.subheader("Personal Info")
        st.write(f"Name: {player_info['player_name'].iloc[0]}")
        st.write(f"Age: {int(player_info['age'].iloc[0])}")
        st.write(f"Status: {player_info['status'].iloc[0]}")

    # Physical Attributes
    with col2:
        st.subheader("Physical Attributes")
        st.write(f"Height: {int(player_info['height'].iloc[0])}")
        st.write(f"Weight: {int(player_info['weight'].iloc[0])}")

    # Professional Details
    with col3:
        st.subheader("Professional Details")
        st.write(f"Team: {player_info['team'].iloc[0]}")
        st.write(f"Jersey Number: {int(player_info['jersey_number'].iloc[0])}")

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
    # Sidebar for Page Selection - Moved here to be under the player's photo
    page = st.sidebar.selectbox(
        "Choose a Page",
        ["Player Info and Prediction", "Season Schedule and Injury Indicator"],
    )

    return player_info, page


########################################################
##                      Injury Tab                    ##
# REF: https://docs.streamlit.io/library/cheatsheet   ##
########################################################


# Function to show injury prediction visualization
def show_injury_prediction(player_info, injury_data):
    st.header("Injury Prediction Visualization")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Injury History")

        if not player_info.empty:
            player_name = player_info["player_name"].iloc[0]
            player_name_lower = player_name.lower()  # Convert to lowercase for matching

            # Filter the injury data for the selected player
            player_injuries = injury_data[
                injury_data["Full Name Lower"] == player_name_lower
            ]

            if not player_injuries.empty:
                st.write(f"2020-2022 Injury History for {player_name}:")
                # Set 'Season' as the index
                if (
                    "Season" in player_injuries.columns
                ):  # Check if 'Season' column exists
                    player_injuries = player_injuries.set_index("Season")
                st.write(
                    player_injuries[["Injury Category", "Counts"]].reset_index(
                        drop=True
                    )
                )
            else:
                st.write(f"No injury data available for {player_name}.")
        else:
            st.write("Please select a player.")

    with col2:
        st.subheader("Injury Prediction for This Year")
        # if not player_info.empty:
        #     player_name = player_info["player_name"].iloc[0].lower()
        #     prediction = predictions[predictions["Player Name"] == player_name]

        #     if not prediction.empty:
        #         # Example: Assuming prediction has a column 'Injury Likelihood' with boolean values
        #         likelihood = prediction["Injury Likelihood"].iloc[0]

        #         # Custom bar chart using Matplotlib
        #         fig, ax = plt.subplots()
        #         bars = ax.bar(
        #             ["Injury Prediction"], [1], color="red" if likelihood else "grey"
        #         )
        #         ax.set_yticks([])
        #         ax.set_xticks([])
        #         plt.box(False)
        #         st.pyplot(fig)

        #         # Textual Prediction
        #         prediction_text = "Highly Likely" if likelihood else "Unlikely"
        #         st.write(f"Injury Prediction: {prediction_text}")
        #     else:
        #         st.write("No prediction data available for this player.")
        # else:
        #     st.write("Please select a player.")


##########################################
## Season Section                       ##
##########################################
def get_player_schedule(player_info, schedule):
    if not player_info.empty:
        player_team = player_info["team"].iloc[0]
        player_schedule = schedule[
            (schedule["Home Team"] == player_team)
            | (schedule["Visitor Team"] == player_team)
        ]

        # Convert 'season' to int and then to string to avoid formatting with commas
        player_schedule["Season"] = player_schedule["Season"].astype(int).astype(str)

        player_schedule = player_schedule.set_index("Week")
        return player_schedule
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no player is selected


# Function to show season schedule
def show_season_schedule(player_info, schedule):
    st.header("Season Schedule")

    player_schedule = get_player_schedule(player_info, schedule)

    if not player_schedule.empty:
        st.write(player_schedule)
    else:
        st.write("No schedule data available for the selected player.")


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
    st.title("2022 NFL Injury Player Cards")

    # Call show_player_info and get the player info and selected page
    player_info, page = show_player_info()
    injury_data = load_injuries()
    schedule = load_schedule()

    # Call the relevant functions based on page selection
    if page == "Player Info and Prediction":
        show_injury_prediction(player_info, injury_data)
    elif page == "Season Schedule and Injury Indicator":
        show_season_schedule(player_info, schedule)
        show_weather_stadium_info()
        show_injury_indicator()


if __name__ == "__main__":
    main()
