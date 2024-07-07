import Helper as req
import json
import pandas as pd
from pandas import DataFrame

# GLOBAL VARIABLES

matches_file = "matches.json"
api_key = "RGAPI-1dc2f54b-a46b-44ec-8d6c-910ef2fbdf24"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = req.fetch_account_puuid(gameName, tagline, api_key)
print(puuid)



def update(filename = "data.csv"):

    # UPDATE MATCHES
    req.update_matches(puuid, api_key)

    # FETCH MATCH LIST
    idx, _, matchlist = req.json_to_matches(matches_file)
    
    data = pd.read_csv(filename)
    if data.empty:
        data = pd.DataFrame()
    
    # PARSE THROUGH NEW MATCHES AND UPDATE DATA
    for i in range(idx, 10):
        match_json = req.fetch_match_details(match_id = matchlist[i], api_key= api_key)
        matchDF = req.process_match_details(match = match_json, puuid = puuid)
        data = pd.concat([data, matchDF])

    data.to_csv(filename, index = False)

update()


