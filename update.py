import Helper as req
import json

matches_file = "matches.json"

with open("info.json", "r") as json_file:
    data = json.load(json_file)

puuid = data.get("puuid")

api_key = input("Enter your Riot API Key: ") 

#UPDATE THE DATAFRAME
req.update_data(puuid=puuid, api_key=api_key)