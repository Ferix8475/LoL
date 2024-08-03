import Helper as req
import json

matches_file = "matches.json"
data_file = "data.pkl"
results_file = "results.json"
info_file = "info.json"
region = "americas" # CHANGE IF NEEDED

api_key = input("Enter your Riot API Key: ") 
riot_id = input("Enter your Riot ID: ") 

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

#Fetch PUUID
puuid = req.fetch_account_puuid(gameName=gameName, tagLine= tagline, api_key=api_key, region = region)

with open(info_file, 'w') as json_file:
    info = {
        riot_id: riot_id,
        puuid: puuid
    }
    json.dump(info, json_file)

req.update_data(puuid = puuid, api_key=api_key, datafile = data_file, matcheS_file = matches_file, new = True)
