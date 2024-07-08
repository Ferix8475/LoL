import Helper as req
import json
import pandas as pd
from pandas import DataFrame

# GLOBAL VARIABLES

matches_file = "matches.json"
data_file = "data.pkl"
results_file = "results.json"
api_key = "RGAPI-1dc2f54b-a46b-44ec-8d6c-910ef2fbdf24"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = req.fetch_account_puuid(gameName, tagline, api_key)


# UPDATE THE DATAFRAME
req.update_data(puuid=puuid, api_key=api_key)

df = pd.read_pickle(data_file)
# Group by Champion and Role
grouped = df.groupby(['Champion', 'Role'])

# Calculate win rate
win_rate = grouped['Win'].mean().reset_index(name='Win Rate')

# Calculate average KDA for wins and losses
avg_kda_wins = grouped.apply(lambda x: x[x['Win']]['KDA'].mean()).reset_index(name='Avg KDA - Wins')
avg_kda_losses = grouped.apply(lambda x: x[~x['Win']]['KDA'].mean()).reset_index(name='Avg KDA - Losses')

# Calculate average dragons killed for wins and losses
avg_dragons_wins = grouped.apply(lambda x: x[x['Win']]['Dragons_Killed'].mean()).reset_index(name='Avg Dragons Killed - Wins')
avg_dragons_losses = grouped.apply(lambda x: x[~x['Win']]['Dragons_Killed'].mean()).reset_index(name='Avg Dragons Killed - Losses')

# Merge average statistics for wins and losses
merged_avg_stats = pd.merge(avg_kda_wins, avg_kda_losses, on=['Champion', 'Role'], how='outer')
merged_avg_stats = pd.merge(merged_avg_stats, avg_dragons_wins, on=['Champion', 'Role'], how='outer')
merged_avg_stats = pd.merge(merged_avg_stats, avg_dragons_losses, on=['Champion', 'Role'], how='outer')

# Merge win rate with average statistics
merged_stats = pd.merge(win_rate, merged_avg_stats, on=['Champion', 'Role'], how='outer')
print(merged_stats)