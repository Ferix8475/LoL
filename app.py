from flask import Flask, jsonify, render_template, request, send_from_directory
import pandas as pd
import Helper as req
import os

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
#req.update_data(puuid=puuid, api_key=api_key)
df = pd.read_pickle(data_file)



"""
Data Retrieval
"""
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


"""
Image Retrieval
"""
def get_images_from_folder(folder_path):
    try:
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        return image_files
    except Exception as e:
        return {'error': str(e)}

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)

@app.route('/api/images')
def get_images():
    folder = request.args.get('folder', 'general/poro')
    image_folder = os.path.join('static/images', folder)
    image_files = get_images_from_folder(image_folder)
    if 'error' in image_files:
        return jsonify({'error': image_files['error']}), 500
    return jsonify(image_files)

"""
Data Retrieval
"""
@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    print(data)
    info = get_champion_data(data['championName'], data['role'])
    exists = any(info.values())

    if exists:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
    


"""
Template Rendering
"""
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/champion')
def champion():
    return render_template('champion.html')

if __name__ == '__main__':
    app.run(debug=True)































