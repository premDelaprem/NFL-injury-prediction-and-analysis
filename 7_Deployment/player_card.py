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
    predictions = pd.read_csv("./configs/player_modeling_data.csv")
    # Ensure that the player name is in the same format as used in player_info
    predictions["Player Name"] = predictions["full_name"].str.lower()  # If needed
    return predictions


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

        return extract_date_from_game_id(schedule)  # Call the date extraction function
    except Exception as e:
        st.error(f"Error loading schedule data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


# Function to extract date from game_id
def extract_date_from_game_id(schedule):
    try:
        # Convert game_id to string
        schedule["game_id_str"] = schedule["Game ID"].astype(str)

        # Extract the date part (first 8 characters) and convert to datetime
        schedule["Game_Date"] = pd.to_datetime(
            schedule["game_id_str"].str[:8], format="%Y%m%d"
        )

        if "Game_Date" not in schedule.columns:
            raise ValueError("Game_Date column not added to schedule")

        return schedule
    except Exception as e:
        st.error(f"Error extracting dates from game_id: {e}")
        return pd.DataFrame()


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
    weather_df["game_id"] = weather_df["Game_Date"].dt.strftime("%Y%m%d")
    # weather_df["game_id"] = weather_df["Game_Date"].astype(str).str[:10]
    weather_df = weather_df[weather_df["Year"].isin([2020, 2021, 2022])]

    return weather_df


# Load Stadium Coordinates
@st.cache_data
def load_stadium_coordinates():
    url = "https://raw.githubusercontent.com/ThompsonJamesBliss/WeatherData/master/data/stadium_coordinates.csv"
    stadium_data = pd.read_csv(url)
    return stadium_data


@st.cache_data
def get_team_name_mapping():
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
    return team_name_mapping


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

    # Load predictions
    predictions = load_predictions()

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

        if not player_info.empty:
            player_name = player_info["player_name"].iloc[0].lower()
            prediction = predictions[predictions["Player Name"] == player_name]

            if not prediction.empty:
                # Example: Assuming prediction has a column 'Injury Likelihood' with boolean values
                likelihood = prediction["Injured_in_2022"].iloc[0]

                # Custom bar chart using Matplotlib
                fig, ax = plt.subplots()
                bars = ax.bar(
                    ["Injury Prediction"], [1], color="red" if likelihood else "green"
                )
                ax.set_yticks([])
                ax.set_xticks([])
                plt.box(False)
                st.pyplot(fig)

                # Textual Prediction
                prediction_text = "Highly Likely" if likelihood else "Unlikely"
                st.write(f"Injury Prediction: {prediction_text}")
            else:
                st.write("No prediction data available for this player.")
        else:
            st.write("Please select a player.")


##########################################
## Season Schedule Section              ##
##########################################
# Functin to get player schedule
def get_player_schedule(player_info, schedule):
    if not player_info.empty:
        player_team = player_info["team"].iloc[0]
        player_schedule = schedule.loc[
            (schedule["Home Team"] == player_team)
            | (schedule["Visitor Team"] == player_team),
            [
                "Week",
                "Season",
                "Home Team",
                "Visitor Team",
                "Home Final Score",
                "Visitor Final Score",
                "Game ID",
            ],
        ].copy()
        # Set 'Week' as the index
        player_schedule.set_index("Week", inplace=True)
        return player_schedule
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no player is selected


# Function to show season schedule
def show_season_schedule(
    player_info, schedule, weather_data, stadium_data, team_name_mapping
):
    st.header("Season Schedule")

    player_schedule = get_player_schedule(player_info, schedule)

    if not player_schedule.empty:
        # Resetting index if 'Week' is set as index
        player_schedule.reset_index(inplace=True)

        # Display the selected columns for the full season schedule
        st.write("Full Season Schedule:")
        player_schedule_display = player_schedule.rename(
            columns={
                "Home Team": "Home Team Full",
                "Visitor Team": "Away Team Full",
                "Home Final Score": "Home Final Score",
                "Visitor Final Score": "Away Final Score",
                "Game ID": "game_id_str",
            }
        )
        player_schedule_display = player_schedule_display[
            [
                "Week",
                "Season",
                "Home Team Full",
                "Home Final Score",
                "Away Team Full",
                "Away Final Score",
            ]
        ]
        st.write(player_schedule_display.reset_index(drop=True))

        # Adding a week selector below the full schedule
        st.subheader("Select a Week for Detailed Information")
        week_options = player_schedule["Week"].unique().tolist()
        selected_week = st.slider(
            "Week",
            min_value=min(week_options),
            max_value=max(week_options),
            value=min(week_options),
        )
        # Filter the schedule for the selected week
        week_games = player_schedule[player_schedule["Week"] == selected_week]

        # Display weather and stadium info for the selected week
        if selected_week in week_options:
            display_weather_stadium_info(week_games)  # Pass the filtered DataFrame
        else:
            st.write("Selected week not available in schedule.")


##########################################
## Weather Stadium Section              ##
##########################################
def merge_data(schedule, weather_data, stadium_data, team_name_mapping):
    # Convert team abbreviations to full names in schedule
    schedule["Home_Team_Full"] = schedule["Home Team"].map(team_name_mapping)
    schedule["Away_Team_Full"] = schedule["Visitor Team"].map(team_name_mapping)

    # Merge schedule with weather data
    merged_schedule = pd.merge(
        schedule,
        weather_data,
        left_on=["Game Date", "Home_Team_Full", "Away_Team_Full"],
        right_on=["Game Date", "Home_Team", "Away_Team"],
        how="left",
    )

    # Merge with stadium data
    merged_schedule = pd.merge(
        merged_schedule,
        stadium_data,
        left_on="Home_Team_Full",
        right_on="HomeTeam",
        how="left",
    )

    return merged_schedule


def merge_schedule_with_weather_data(schedule, weather_data, team_name_mapping):
    # Convert team abbreviations to full names
    schedule["Home_Team_Full"] = schedule["Home Team"].map(team_name_mapping)
    schedule["Visitor_Team_Full"] = schedule["Visitor Team"].map(team_name_mapping)

    # Ensure date formats are consistent
    schedule["Game_Date"] = pd.to_datetime(schedule["Game_Date"])
    weather_data["Game_Date"] = pd.to_datetime(weather_data["Date_Time"]).dt.strftime(
        "%Y%m%d"
    )
    weather_data["Game_Date"] = pd.to_datetime(weather_data["Game_Date"])

    # Merge the dataframes
    merged_data = pd.merge(
        schedule,
        weather_data,
        left_on=["Game_Date", "Home_Team_Full", "Visitor_Team_Full"],
        right_on=["Game_Date", "Home_Team", "Away_Team"],
        how="left",
    )
    return merged_data


def display_weather_stadium_info(week_games):
    for _, week_game in week_games.iterrows():
        # Display game details
        game_id = week_game.get("Game ID")
        home_team = week_game.get("Home Team")
        away_team = week_game.get("Visitor Team")
        st.write(f"Game ID: {game_id}, Home Team: {home_team}, Away Team: {away_team}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Weather Information")
            if "Temperature" in week_game and "Weather_Condition" in week_game:
                temperature = week_game["Temperature"]
                weather_condition = week_game["Weather_Condition"]
                st.write(f"Temperature: {temperature}")
                st.write(f"Weather Condition: {weather_condition}")
            else:
                st.write("Weather information not available")

        with col2:
            st.subheader("Stadium Information")
            if "StadiumName" in week_game and "RoofType" in week_game:
                stadium_name = week_game["StadiumName"]
                roof_type = week_game["RoofType"]
                st.write(f"Stadium: {stadium_name}")
                st.write(f"Roof Type: {roof_type}")
            else:
                st.write("Stadium information not available")


##########################################
## Injury Section                       ##
##########################################


# Function to show another injury indicator
def show_injury_indicator():
    st.header("Injury Indicator")

    # Create a dropdown to select the image
    selected_image = st.selectbox(
        "Select an Injury Indicator Image",
        [
            "Severe Lower Body Injuries by Surface Type",
            "Lower Body Injuries per Play Type and Surface",
            "Lower Body Injuries per Position by Surface Type",
            "Lower Body Injuries by Surface Type",
            "Distribution of Play Number",
        ],
    )

    # Define a dictionary to map the selected option to the corresponding image path
    image_paths = {
        "Severe Lower Body Injuries by Surface Type": "./src/severe_inj_by_surface.jpeg",
        "Lower Body Injuries per Play Type and Surface": "./src/play_type_injs.jpeg",
        "Lower Body Injuries per Position by Surface Type": "./src/inj_position_surface.jpeg",
        "Lower Body Injuries by Surface Type": "./src/inj_by_surface.jpeg",
        "Distribution of Play Number": "./src/distribution_play_num.jpeg",
    }

    # Display the selected image
    if selected_image in image_paths:
        st.image(image_paths[selected_image], caption=selected_image)
    else:
        st.write("Please select an image from the dropdown menu.")


##########################################
## Injury Section                       ##
##########################################


# Main App
def main():
    st.title("2022 NFL Injury Player Cards")

    # Retrieve the team name mapping
    team_name_mapping = get_team_name_mapping()

    # Retrieve player info and the selected page
    player_info, page = show_player_info()

    # Load various datasets
    injury_data = load_injuries()
    schedule = load_schedule()
    weather_data = load_stadium_weather()
    stadium_data = load_stadium_coordinates()

    # Display content based on the selected page
    if page == "Player Info and Prediction":
        show_injury_prediction(player_info, injury_data)
    elif page == "Season Schedule and Injury Indicator":
        # Merge schedule with weather data
        merged_schedule = merge_schedule_with_weather_data(
            schedule, weather_data, team_name_mapping
        )

        # Display the season schedule, including the team name mapping
        show_season_schedule(
            player_info, merged_schedule, weather_data, stadium_data, team_name_mapping
        )

        # Show additional injury indicator if needed
        show_injury_indicator()


if __name__ == "__main__":
    main()
