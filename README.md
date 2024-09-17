# fantasy-soccer


 Repository for collecting & analyzing Premier League Soccer data

Goal: 
     - Using the insights generated from this data, I'd like to make a predictive model for PL matchups
     - Learn more about applications for statistics (probabilaties, modeling, etc.)

Contents:

 - Analysis: Folder for research and analysis
 - Engineering: Where pipeline & data flow scripts are held. Most of this setup is still ad hoc jupyter notebooks, since most of the data I need is backfill from 2022 or 2023. Will make a more production-ready pipeline when I need automatic updating or need the data to go somewhere live.
 - Simulator: Where I'm housing simulation code
    - sim_v1: concept for team vs team goal & performance estimation. Uses basic aggregation of player abilities to estimate pass, keep, disposession, or shot events every 4 seconds for a game. Parameters for how often an event occurs is still arbitrarily defined, and all assessment is done at the team level, giving no consideration to where an event may be taking place on the field.



old notes:

players.ipynb is to pull pre-draft player data
explorer.ipynb is to test other endpoints available

next steps:
 - get player schedules
 - forecast difficulty of a future player's week
 - get my own team data & free agency data
 - pick what available players will have the easiest week compared to their ppg/ppm and opponent difficulty

 - any way to scrape starting lineups to see if a player is even playing?
 - reddit/social media sentiment?