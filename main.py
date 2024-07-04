import requests
import Helper
import json


# GLOBAL VARIABLES

matches_file = "matches.json"
api_key = "RGAPI-832bd063-06b6-4a96-b7a2-d76e7015b0a4"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = Helper.fetch_account_puuid(gameName, tagline, api_key)


# UPDATE MATCHES
#matches = Helper.fetch_all_matches(puuid = puuid, api_key = api_key)
#Helper.matches_to_json(matchlist=matches, api_key = api_key)
latest, matchlist = Helper.json_to_matches("matches.json")
print(latest, matchlist)