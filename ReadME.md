# Project: Analyzing and Predicting Injuries in the NFL

### Developed by: Kyera Francis, Jack Frantz, and Prem Patel

### Overview:
The NFL is an extremely high contact sport, and every year there are hundreds of injuries that jeopardize not only the team's chances at success, but also, and more importantly, the player’s long term health and careers. There are numerous factors that can be attributed to whether an injury will occur in any given game. However, we want to find out if there are some circumstances that are more associated with higher occurrences of injury such as the surface, position, and/or type of play that was called when an injury occurred. Additionally, we want to investigate whether we can accurately predict a **specific** player’s risk of injury.


### Problem Statement:
With season, and potentially career, ending injuries on the rise, the NFL, in association with ESPN and SportsCenter, has contracted the 3 of us to investigate playing circumstances and draw any associations to lower body injuries. Additionally, we have also been asked to create a preliminary model to see whether we can accurately predict a given NFL player’s likelihood of injury. Prior to beginning, we had two hypotheses. First, we believed that injuries could strongly be associated with conditions like field type, position, and how many times a player is utilized in a game. Second, we believed that we could create a predictive model suggesting the likelihood of injury for a given player based on their past injury history and some statistics regarding their age, weight, height, and position.


### Key Focus Areas
- **Data Utilization**: The modeling for player injury predictions will leverage historical injury data agregated from weekly NFL injury reports. Both injury type and frequency for each player will be taken into account to predict future injury occurances. In the future, data such as player performance metrics and training intensity can be added to potentially improve modeling. For added context, data on game conditions like weather, field material, and stadium type was analyzed to find connections to injury occurance and severity.
- **Analysis and Pattern Recognition**: By analyzing patterns and correlations within the data, the model will provide insights into the key risk factors contributing to injuries.
- **Injury Prevention Strategies**: Utilizing the insights gained, the team can implement more effective injury prevention strategies, optimizing player health management and reducing the likelihood of injuries.

### Project Organization
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

### Dataset link & description
- [NFL Injury Data](https://www.kaggle.com/datasets/jpmiller/nfl-competition-data)
  - This dataset supports the Big Data Bowl 2023. You'll find new data gathered and aggregated via various APIs and scrapes:
  - Weekly team rosters
  - Play-by-play data with features related to rushing and tackles
  - Charting data by play and game (see specific licensing terms),
  - Injury data
  - Data from the NFL Combine event 
  
  The data was collected by JohnM and is available on Kaggle.


- [NFL Play by Play Injury Data](https://www.kaggle.com/competitions/nfl-playing-surface-analytics/data)
    - This dataset is separately taken from another competition hosted by the NFL, NFL 1st and Future - Analytics, and contains:
    - 105 lower body injury records from 2 subsequent seasons
    - Play-by-play data with information like weather, temperature, play type, position involved, bodily part injured, etc.
    - Player track data (***this we did not utilize***)
    
    
### Summarizing Analysis and Findings
Upon reviewing the performance metrics of out Logistic Regression model, we have observed the following outcomes:
- The model’s accuracy is approx. 83%, which implies a reasonably high right of correct predictions for injury. We recognize that accuracy is not the most appropriate indicator of performance especially since our data set was imbalance (80/20)
- The model’s precision of our model is approx. 43%, which reflects the proportion of true positives in all positive predictions in this model. This is a great start but leaves great room for improvement, as the majority of the predictions were false positives. 
    - As a note, because we assume our clients will rather offer preventative measures even if the predictions are not precise this measurement is the focus of our analysis.
- The model’s recall is approx. 23%, the model demonstrated a less than average outcome of identifying actual injury instances. This metric allows us to understand where our model is lacking and what methods can be implemented to improve the results of our model overall. 
- Finally, our model’s F1 Score was approx. 30%. This metric shows the lack of balance in our precision and recall scores and with the implemented suggestions for improving the robustness of our model we believe that we can increase our model’s performance to a standard that is acceptable for real-world use.  