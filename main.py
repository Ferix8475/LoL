import Helper as req
import json
import pandas as pd

# GLOBAL VARIABLES

matches_file = "matches.json"
api_key = "RGAPI-1dc2f54b-a46b-44ec-8d6c-910ef2fbdf24"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = req.fetch_account_puuid(gameName, tagline, api_key)
print(puuid)



def update():

    # UPDATE MATCHES
    req.update_matches(puuid, api_key)

    # FETCH MATCH LIST
    idx, _, matchlist = req.json_to_matches(matches_file)
    print(len(matchlist))

    # PARSE THROUGH NEW MATCHES AND UPDATE DATA
    timeline_data = req.fetch_match_details(match_id=matchlist[idx], api_key=api_key)
    frames = timeline_data['info']
   

    print(frames)


update()


