"""
# Player Card App - Streamlit 
# Inspired by: https://docs.streamlit.io/get-started, https://www.youtube.com/playlist?list=PLJJOI_ZUeaBphhaFWf2fotnKhF95MdI4g
# Weather information: https://www.datawithbliss.com/weather-data & https://github.com/ThompsonJamesBliss/WeatherData
# Weather library documentation: https://dev.meteostat.net/python/monthly.html#api
## Placed exceptions in the code to avoid errors when loading data that required either a connection or a merge
#Import Libraries
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from meteostat import Point, Daily, Hourly
from datetime import datetime


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


# Player Schedule
@st.cache_data
def extract_date_from_game_id(schedule):
    try:
        # Convert game_id to string
        schedule["game_id_str"] = schedule["Game ID"].astype(str)

        # Extract the date part (first 8 characters) and convert to datetime
        schedule["Game_Date"] = pd.to_datetime(
            schedule["game_id_str"].str[:8], format="%Y%m%d"
        )
        schedule = extract_date_from_game_id(schedule)
        if "Game_Date" not in schedule.columns:
            raise ValueError("Game_Date column not added to schedule")

        return schedule
    except Exception as e:
        st.error(f"Error loading schedule data: {e}")
        return pd.DataFrame()


# Team Schedule
@st.cache_data
def load_schedule():
    try:
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
                "gameId",
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
                "gameId": "Game ID",
            }
        )

        # Convert 'Season' to string to avoid formatting with commas
        schedule["Season"] = schedule["Season"].astype(int).astype(str)

        # Extract the date from game_id
        schedule = extract_date_from_game_id(schedule)

        return schedule
    except Exception as e:
        st.error(f"Error loading schedule data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


# Load Game Data
@st.cache_data
def load_game():
    url = "https://raw.githubusercontent.com/ThompsonJamesBliss/WeatherData/master/data/games.csv"
    games_df = pd.read_csv(url)
    filtered_games_df = games_df[games_df["Season"].isin([2020, 2021, 2022])]
    return filtered_games_df


# Load Weather Data
@st.cache_data
def load_stadium_weather():
    csv_path = "./src/nfl_weather_data.csv"  # Adjust the path if necessary
    weather_df = pd.read_csv(csv_path)
    # Removing timezone information from the 'Date_Time' column
    weather_df["Date_Time"] = weather_df["Date_Time"].str.rsplit(" ", 1).str[0]
    # Convert the 'Date_Time' column to datetime objects
    weather_df["Game_Date"] = pd.to_datetime(
        weather_df["Date_Time"], format="%m/%d/%y %I:%M %p"
    )

    # Extract the year from TimeMeasure and filter based on the year
    weather_df["Year"] = weather_df["Game_Date"].dt.year
    weather_df = weather_df[weather_df["Year"].isin([2020, 2021, 2022])]

    return weather_df


# Load Stadium Coordinates
@st.cache_data
def load_stadium_coordinates():
    url = "https://raw.githubusercontent.com/ThompsonJamesBliss/WeatherData/master/data/stadium_coordinates.csv"
    stadium_data = pd.read_csv(url)
    return stadium_data


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
## Season Schedule Section              ##
##########################################
# Functin to get player schedule
def get_player_schedule(player_info, schedule):
    if not player_info.empty:
        player_team = player_info["team"].iloc[0]
        player_schedule = schedule[
            (schedule["Home Team"] == player_team)
            | (schedule["Visitor Team"] == player_team)
        ]

        # Ensure 'gameId' is included
        player_schedule = player_schedule.set_index("Week")[
            ["Season", "Game ID", "Home Team", "Visitor Team", "Game Date"]
        ]
        player_schedule["Game ID"] = player_schedule["Game ID"].astype(str)

        return player_schedule
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no player is selected


# Function to show season schedule
def show_season_schedule(player_info, schedule, weather_data, stadium_data):
    st.header("Season Schedule")
    # Loading Team Names
    team_name_mapping = {
        "ARI": "Cardinals",
        "ATL": "Falcons",
        "BAL": "Ravens",
        "BUF": "Bills",
        "CAR": "Panthers",
        "CHI": "Bears",
        "CIN": "Bengals",
        "CLE": "Browns",
        "DAL": "Cowboys",
        "DEN": "Broncos",
        "DET": "Lions",
        "GB": "Packers",
        "HOU": "Texans",
        "IND": "Colts",
        "JAX": "Jaguars",
        "KC": "Chiefs",
        "LAC": "Chargers",
        "LAR": "Rams",
        "LV": "Raiders",
        "MIA": "Dolphins",
        "MIN": "Vikings",
        "NE": "Patriots",
        "NO": "Saints",
        "NYG": "Giants",
        "NYJ": "Jets",
        "PHI": "Eagles",
        "PIT": "Steelers",
        "SF": "49ers",
        "SEA": "Seahawks",
        "TB": "Buccaneers",
        "TEN": "Titans",
        "WAS": "Washington",
    }
    # Merge the schedule and weather data
    merged_schedule = merge_schedule_with_weather(
        schedule, weather_data, team_name_mapping
    )

    player_schedule = get_player_schedule(player_info, schedule)

    if not player_schedule.empty:
        # Display the full season schedule
        st.write("Full Season Schedule:")
        player_schedule["Game_Date"] = player_schedule["Game Date"].astype(str).str[:10]
        st.write(player_schedule.drop(columns=["Game ID"]).reset_index())

        # Adding a week selector below the full schedule
        st.subheader("Select a Week for Detailed Information")
        week_options = player_schedule.index.tolist()
        selected_week = st.slider(
            "Week",
            min_value=week_options[0],
            max_value=week_options[-1],
            value=week_options[0],
        )
        # Validate if selected week is in the player_schedule
    if selected_week in player_schedule.index:
        display_weather_stadium_info(
            selected_week, player_schedule, weather_data, stadium_data
        )
    else:
        st.write("Selected week not available in schedule.")


##########################################
## Weather Stadium Section              ##
##########################################
def merge_schedule_with_weather(schedule, weather_data, team_name_mapping):
    # Convert team names in the schedule to full names using the mapping
    schedule["Home_Team_Full"] = schedule["Home Team"].map(team_name_mapping)
    schedule["Away_Team_Full"] = schedule["Visitor Team"].map(team_name_mapping)

    # Preprocess the date in weather data to match the schedule data
    weather_data["Game_Date"] = pd.to_datetime(weather_data["Date_Time"]).dt.strftime(
        "%Y%m%d"
    )

    # Create a unique identifier in both dataframes for merging
    schedule["Game_Identifier"] = (
        schedule["Game_Date"].astype(str)
        + schedule["Home_Team_Full"]
        + schedule["Away_Team_Full"]
    )
    weather_data["Game_Identifier"] = (
        weather_data["Game_Date"].astype(str)
        + weather_data["Home_Team"]
        + weather_data["Away_Team"]
    )

    # Merge the dataframes on the identifier
    merged_df = pd.merge(schedule, weather_data, on="Game_Identifier", how="left")

    return merged_df


def merge_data(game_data, weather_data, stadium_data):
    try:
        # Convert game_id to string before merging
        player_schedule["Game ID"] = player_schedule["Game ID"].astype(str)
        weather_data["game_id"] = weather_data["game_id"].astype(str)

        # Ensure all datasets are loaded correctly
        if game_data.empty or weather_data.empty or stadium_data.empty:
            raise ValueError("One or more datasets are empty")

        # Merge game data with weather data based on common keys
        merged_data = pd.merge(game_data, weather_data, on=["game_id"], how="left")

        # Merge with stadium data on HomeTeam
        merged_data = pd.merge(merged_data, stadium_data, on="HomeTeam", how="left")

        return merged_data
    except Exception as e:
        st.error(f"Error merging data: {e}")
        return pd.DataFrame()


# Function to show weather and stadium information
def fetch_weather_for_game(stadium_info, game_date):
    try:
        # Extract latitude and longitude
        lat = stadium_info["Latitude"].iloc[0]
        lon = stadium_info["Longitude"].iloc[0]

        # Create Point for Meteostat
        location = Point(lat, lon)

        # Get weather data for the game day
        weather = Daily(location, game_date, game_date)
        weather = weather.fetch()

        return weather
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return pd.DataFrame()


def display_weather_stadium_info(
    selected_week, player_schedule, weather_data, stadium_data
):
    if player_schedule.empty:
        st.write("Player schedule is empty. No data to display.")

        return

    try:
        week_games = player_schedule.loc[selected_week]

        # Handle case where there's only one game in the week
        if not isinstance(week_games, pd.DataFrame):
            week_games = week_games.to_frame().T

        for _, week_game in week_games.iterrows():
            game_id = week_game["Game ID"]
            home_team = week_game["Home Team"]

            # Fetch game weather and stadium info
            game_weather = weather_data[weather_data["game_id"] == game_id]
            stadium_info = stadium_data[stadium_data["HomeTeam"] == home_team]

            # Debug statements
            # Print the data types and some values for game_id in both DataFrames
            st.write(
                "Player Schedule 'Game ID' Type:", player_schedule["Game ID"].dtype
            )
            st.write("Weather Data 'game_id' Type:", weather_data["game_id"].dtype)
            st.write(
                "Player Schedule 'Game ID' Sample:", player_schedule["Game ID"].head()
            )
            st.write("Weather Data 'game_id' Sample:", weather_data["game_id"].head())

            if not stadium_info.empty and not game_weather.empty:
                game_date = week_game["Game_Date"]
                st.subheader(f"Weather and Stadium Information for Game on {game_date}")

                col1, col2 = st.columns(2)  # Create two columns

                with col1:
                    # Weather Information
                    st.subheader("Weather Information")
                    temp_celsius = game_weather["tavg"].iloc[0]
                    temp_fahrenheit = temp_celsius * 9 / 5 + 32
                    st.write(f"Temperature: {temp_fahrenheit:.1f}°F")
                    st.write(f"Precipitation: {game_weather['prcp'].iloc[0]} mm")
                    st.write(f"Wind Speed: {game_weather['wspd'].iloc[0]} km/h")

                with col2:
                    # Stadium Information
                    st.subheader("Stadium Information")
                    st.write(f"Stadium: {stadium_info['StadiumName'].iloc[0]}")
                    st.write(f"Roof Type: {stadium_info['RoofType'].iloc[0]}")
            else:
                st.write(
                    "Complete weather or stadium information not available for this game."
                )

    except KeyError as e:
        st.write(f"Missing data for key {e}.")
    except Exception as e:
        st.error(f"Error displaying weather and stadium information: {e}")


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
    weather_data = load_stadium_weather()
    stadium_data = load_stadium_coordinates()

    # Call the relevant functions based on page selection
    if page == "Player Info and Prediction":
        show_injury_prediction(player_info, injury_data)
    elif page == "Season Schedule and Injury Indicator":
        show_season_schedule(player_info, schedule, weather_data, stadium_data)
        show_injury_indicator()


if __name__ == "__main__":
    main()
