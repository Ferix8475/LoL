import Helper as req
import json
import os

matches_file = "matches.json"
data_file = "data.pkl"
results_file = "results.json"
info_file = "info.json"
region = "americas" # CHANGE IF NEEDED

api_key = input("Enter your Riot API Key: ") 
riot_id = input("Enter your Riot ID (gamename#tagline): ") 

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

#Fetch PUUID
puuid = req.fetch_account_puuid(gameName=gameName, tagLine= tagline, api_key=api_key, region = region)

with open(info_file, 'w') as json_file:
    info = {
        riot_id: riot_id,
        puuid: puuid
    }
    json.dump(info, json_file, indent = 4)

# Setup matches.json to be properly formatted
with open("matches.json", "w") as json_file:
    matches = {
        "latest": 0,
        "matchlist": []
    }
    json.dump(matches, json_file, indent=4)

# Delete previous data if it exists
if os.path.exists(data_file):
    os.remove(data_file)

# Fetch matches, get data, get everything started
req.update_data(puuid = puuid, api_key=api_key, datafile = data_file, matches_file = matches_file, new = True)
