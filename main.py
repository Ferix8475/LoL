import Helper as req
import json
import pandas as pd
from pandas import DataFrame
import requests 
import time
# GLOBAL VARIABLES

start = time.time()

matches_file = "matches.json"
data_file = "data.pkl"
results_file = "results.json"
api_key = "RGAPI-987c33b6-6a1e-4a6f-93a4-a8edef2bd4ae"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = "UgcPcMMVvDTOrgu68pkfhZqszLwqYckwUTpLjzjILBa2PtgMN2xI2opciuwdqrNZhhwz66JVhmCfGA"

# UPDATE THE DATAFRAME
req.update_data(puuid=puuid, api_key=api_key)

df = pd.read_pickle(data_file)


# Calculate Objective Control Numbers by Champion, Role, and Win
objective_df = df.groupby(['Champion', 'Role', 'Win']).agg({
    'Barons_Killed': 'mean',
    'Void_Grubs_Killed': 'mean',
    'Dragons_Killed': 'mean',
    'Turret_Killed': 'mean',
    'Rift_Heralds_Killed': 'mean',

}).reset_index()
objective_df = req.purge_df(objective_df)


# Calculate the Winrates and Games Played By Role
winrate_by_role = df.groupby(['Champion', 'Role']).agg(
    Winrate=('Win', 'mean'),
    Games_Played=('Win', 'count')
).reset_index()
winrate_by_role = req.purge_df(winrate_by_role)

# Calculate Effectiveness by Wins and Losses
effectiveness_df = df.groupby(['Champion', 'Role', 'Win']).agg({
        'Total_Minions_Killed': 'mean',
        'Total_Jungle_Monsters_Killed': 'mean',
        'Total_Damage_DealtToChampions': 'mean',
        'KDA': 'mean',
        'Kill_Participation': 'mean',
        'Damage_Share': 'mean',
        'Turret_Plates_Taken': 'mean',
        'Gold_Per_Minute': 'mean',
        'Damage_Per_Minute': 'mean',
        'Vision_Score_Per_Minute': 'mean',
        'Lane_Minions_Before_10_Minutes': 'mean',
        'Jungle_CS_Before_10_Minutes': 'mean',
        'Sol_Kills':'mean'

}).reset_index()
effectiveness_df = req.purge_df(effectiveness_df)


# Fetch Runepage ID Matching Dictionaries and Map
runes = req.json_extract_runes()
treepage = {
    8000: "Precision",
    8100: "Domination",
    8200: "Sorcery",
    8300: "Inspiration",
    8400: "Resolve"
}

df['Primary_Tree'] = df['Primary_Tree'].replace(treepage)
df['Secondary_Tree'] = df['Secondary_Tree'].replace(treepage)
df['Primary_Keyston'] = df['Primary_Keystone'].replace(runes)

# Calculate Runepages by Tree Winrates
tree_runes_df = df.groupby(['Champion', 'Role', 'Primary_Tree', 'Secondary_Tree']).agg(
    Winrate=('Win', 'mean'),
    Games_Played=('Win', 'count')
).reset_index()
tree_runes_df = req.purge_df(tree_runes_df)

# Calculate Runepages by Keystone and Secondary Tree Winrates
keystone_runes_df = df.groupby(['Champion', 'Role', 'Primary_Keystone', 'Secondary_Tree']).agg(
    Winrate=('Win', 'mean'),
    Games_Played=('Win', 'count')
).reset_index()
keystone_runes_df_runes_df = req.purge_df(keystone_runes_df)


# Calculate Winrates by Item and Champion
melted_df = df.melt(id_vars=['Champion', 'Win'], value_vars=['Item0', 'Item1', 'Item2', 'Item3', 'Item4', 'Item5', 'Item6'],
                    var_name='ItemSlot', value_name='Item')

melted_df = melted_df[melted_df['Item'] != 0] # Get rid of empty items

item_winrate_df = melted_df.groupby(['Champion', 'Item']).agg(
    Winrate=('Win', 'mean'),
    Games_Played=('Win', 'count')
).reset_index()

mydict = req.json_extract_important_items()

items_to_keep = list(mydict.keys())
item_winrate_df = item_winrate_df[item_winrate_df['Item'].isin(items_to_keep)] # Get rid of unwanted items (components, epic items)

item_winrate_df['Item'] = item_winrate_df['Item'].replace(mydict) # Replace IDs with Names
item_winrate_df = req.purge_df(item_winrate_df)

