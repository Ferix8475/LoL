import Helper as req
import json


# GLOBAL VARIABLES

matches_file = "matches.json"
api_key = "RGAPI-16b44fb0-be55-4f17-ad52-429b76843f32"
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
    timeline_data = req.fetch_match_timeline(match_id=matchlist[idx], api_key=api_key)
    frames = timeline_data.get("info", {}).get("frames", [])
    print(frames[4])
    print(len(frames))

    #print(frames)


update()


