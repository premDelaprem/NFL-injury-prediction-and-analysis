# Project: Predicting the Probability of Injury of NFL Players

### Developed by: Prem Patel, Jack Frantz, and Kyera Francis

## Objective
The primary goal of this project is to develop a predictive model for a professional football analytics team. This model aims to accurately forecast the probability of player injuries in the NFL.

### Key Focus Areas
- **Data Utilization**: The model will leverage historical data, encompassing a wide array of variables such as player performance metrics, training intensity, previous injury history, and game conditions.
- **Analysis and Pattern Recognition**: By analyzing patterns and correlations within the data, the model will provide insights into the key risk factors contributing to injuries.
- **Injury Prevention Strategies**: Utilizing the insights gained, the team can implement more effective injury prevention strategies, optimizing player health management and reducing the likelihood of injuries.
## Project Organization
- **1_DataCollection/**
  - `src/` - Source code for data collection (e.g., APIs, web scraping)
  - `files/` - Raw files downloaded or used during collection
  - `images/` - Images or diagrams explaining the data collection process

- **2_DataCleaning/**
  - `src/` - Source code for data cleaning (e.g., data cleaning scripts)
  - `cleaned_data/` - Output of cleaned data
  - `logs/` - Logs generated during the cleaning process

- **3_DataExploration/**
  - `notebooks/` - Jupyter notebooks for exploratory analysis
  - `reports/` - Reports or summaries of findings
  - `visualizations/` - Initial visualizations used for exploration

- **4_FeatureEngineering/**
  - `src/` - Code for feature engineering (transformations, feature selection)
  - `features/` - Generated feature datasets

- **5_ModelDevelopment/**
  - `models/` - Saved model files (e.g., .pkl for sklearn models)
  - `notebooks/` - Jupyter notebooks for model development and testing
  - `src/` - Additional scripts for model training and validation

- **6_ModelEvaluation/**
  - `results/` - Evaluation results, metrics
  - `visualizations/` - Visualizations of model performance (e.g., ROC curves, confusion matrices)

- **7_Deployment/**
  - `src/` - Code for deploying models (e.g., Flask app, batch scripts)
  - `configs/` - Configuration files for deployment (e.g., .env, Dockerfile)

## Dataset link & description
- [NFL Injury Data](https://www.kaggle.com/datasets/jpmiller/nfl-competition-data)
  - This dataset supports the Big Data Bowl 2023. You'll find new data gathered and aggregated via various APIs and scrapes:
  - Weekly team rosters
  - Play-by-play data with features related to rushing and tackles
  - Charting data by play and game (see specific licensing terms),
  - Injury data
  - Data from the NFL Combine event 
  
  The data was collected by JohnM and is available on Kaggle.
