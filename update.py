import Helper as req
import setup

matches_file = "matches.json"
data_file = "data.pkl"
results_file = "results.json"
api_key = "RGAPI-565659ad-bcd4-4c91-8f9d-7b533a36a0e4"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = "UgcPcMMVvDTOrgu68pkfhZqszLwqYckwUTpLjzjILBa2PtgMN2xI2opciuwdqrNZhhwz66JVhmCfGA"

#UPDATE THE DATAFRAME
req.update_data(puuid=puuid, api_key=api_key)