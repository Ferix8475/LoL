import Helper as req
import json
import pandas as pd
from pandas import DataFrame

# GLOBAL VARIABLES

matches_file = "matches.json"
data_file = "data.pkl"
api_key = "RGAPI-1dc2f54b-a46b-44ec-8d6c-910ef2fbdf24"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = req.fetch_account_puuid(gameName, tagline, api_key)
print(puuid)



def update(datafile = data_file, new = False) -> None:

    # UPDATE MATCHES
    req.update_matches(puuid, api_key)

    # FETCH MATCH LIST
    idx, _, matchlist = req.json_to_matches(matches_file)
    
    if idx == len(matchlist):
        return 
    
    if new:
        data = pd.DataFrame()
    else:
        data = pd.read_pickle(datafile)
    

    # PARSE THROUGH NEW MATCHES AND UPDATE DATA
    try:
        # PARSE THROUGH NEW MATCHES AND UPDATE DATA
        for i in range(idx, len(matchlist)):
            print("New Match, " + str(i))
            match_json = req.fetch_match_details(match_id=matchlist[i], api_key=api_key)
            matchDF = req.process_match_details(match=match_json, puuid=puuid)
            if matchDF is not None:
                data = pd.concat([data, matchDF])
    except Exception as e:
        print(f"Error encountered: {e}") 
        # Server Disconnects/Inconsisitencies with Riot API
    finally:
        data.to_pickle(datafile)
        req.matches_to_json(matchlist=matchlist, api_key=api_key, update_ind=i + 1)
        print(data)

    print(data)

update()
