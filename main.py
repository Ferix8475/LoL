import requests
import Helper
import json


# GLOBAL VARIABLES

matches_file = "matches.json"
api_key = "RGAPI-d31a9a5c-cb66-409c-9d4f-7fa09a8cb666"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = Helper.fetch_account_puuid(gameName, tagline, api_key)
print(puuid)

# UPDATE MATCHES
matches = Helper.fetch_all_matches(puuid = puuid, api_key = api_key)
Helper.matches_to_json(matchlist=matches, api_key = api_key)

_, latest, matchlist = Helper.json_to_matches("matches.json")
print(_, latest, matchlist)
print(len(matchlist))
Helper.update_matches(puuid, api_key)

