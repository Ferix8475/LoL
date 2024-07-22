from flask import Flask, jsonify, render_template, request
import pandas as pd
import Helper as req

app = Flask(__name__)

matches_file = "matches.json"
data_file = "data.pkl"
results_file = "results.json"
api_key = "RGAPI-ece977df-9a74-43a0-b83b-09d98b03dece"
riot_id = "Ferix8475#NA1"

gameName = riot_id.split("#")[0]
tagline = riot_id.split("#")[1]

puuid = "UgcPcMMVvDTOrgu68pkfhZqszLwqYckwUTpLjzjILBa2PtgMN2xI2opciuwdqrNZhhwz66JVhmCfGA"

# UPDATE THE DATAFRAME
req.update_data(puuid=puuid, api_key=api_key)
df = pd.read_pickle(data_file)

# GET THE PROCESSED DATAFRAMES
obj_df, wr_df, stats_df, tree_df, keystone_df, item_df = req.df_to_statdfs(df)

def get_champion_data(champion :str, role: str) -> dict:
    # Filter data for the given champion
    objective_data = obj_df[(obj_df['Champion'] == champion) & (obj_df['Role'] == role)].to_dict(orient='records')
    winrate_data = wr_df[(wr_df['Champion'] == champion) & (wr_df['Role'] == role)].to_dict(orient='records')
    effectiveness_data = stats_df[(stats_df['Champion'] == champion) & (stats_df['Role'] == role)].to_dict(orient='records')
    tree_runes_data = tree_df[(tree_df['Champion'] == champion) & (tree_df['Role'] == role)].to_dict(orient='records')
    keystone_runes_data = keystone_df[(keystone_df['Champion'] == champion) & (keystone_df['Role'] == role)].to_dict(orient='records')
    item_winrate_data = item_df[(item_df['Champion'] == champion)].to_dict(orient='records')

    return {
        "objective_data": objective_data,
        "winrate_data": winrate_data,
        "effectiveness_data": effectiveness_data,
        "tree_runes_data": tree_runes_data,
        "keystone_runes_data": keystone_runes_data,
        "item_winrate_data": item_winrate_data,
    }



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/champion', methods=['POST'])
def champion():
    champion = request.form['champion']
    role = request.form['role']
    data = get_champion_data(champion, role)
    return render_template('champion.html', champion=champion, role=role, data=data)

if __name__ == '__main__':
    app.run(debug=True)































