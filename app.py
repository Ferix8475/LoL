from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
import pandas as pd
import Helper as req
import os

app = Flask(__name__)
"""
Global Variables
"""
data_file = "data.pkl"


global df 
df = pd.read_pickle(data_file)


"""
Data Retrieval
"""
obj_df, wr_df, stats_df, tree_df, keystone_df, item_df = req.df_to_statdfs(df)

def get_champion_data(champion :str, role: str) -> dict:
    """
    Retrieves data associated with champion and role
    """
    objective_data = obj_df[(obj_df['Champion'] == champion) & (obj_df['Role'] == role)].to_dict(orient='records')
    winrate_data = wr_df[(wr_df['Champion'] == champion) & (wr_df['Role'] == role)].to_dict(orient='records')
    effectiveness_data = stats_df[(stats_df['Champion'] == champion) & (stats_df['Role'] == role)].to_dict(orient='records')
    tree_runes_data = tree_df[(tree_df['Champion'] == champion) & (tree_df['Role'] == role)].to_dict(orient='records')
    keystone_runes_data = keystone_df[(keystone_df['Champion'] == champion) & (keystone_df['Role'] == role)].to_dict(orient='records')
    item_winrate_data = item_df[(item_df['Champion'] == champion)].to_dict(orient='records')

    irrelevant_items = {'Stealth Ward', 'Oracle Lens', 'Control Ward', 'Health Potion', 'Elixir of Avarice', 
                        'Elixir of Force', 'Farsight Alteration', 'Elixir of Iron', 'Elixir of Sorcery', 'Elixir of Wrath',
                        'Elixir of Skill', "Doran's Blade", "Doran's Ring", "Doran's Shield", "Cull", "Mosstomper Seedling", "Scorchclaw Pup", 
                        "Gustwalker Hatchling"}
    
    filtered_item_winrate_data = [item for item in item_winrate_data if item['Item'] not in irrelevant_items]

    
    return {
        "objective_data": objective_data,
        "winrate_data": winrate_data,
        "effectiveness_data": effectiveness_data,
        "tree_runes_data": tree_runes_data,
        "keystone_runes_data": keystone_runes_data,
        "item_winrate_data": filtered_item_winrate_data,
    }

"""
Graph Label Retrieval
"""

def get_radar_graph_labels(raw_data: dict) -> dict:
    """
    Returns a dict of the labels and values associated with all of the radar graphs to be created. This includes data on objective control and effectiveness
    """

    objective_data = raw_data['objective_data']
    effectiveness_data = raw_data['effectiveness_data']

    # If there are only Losses or Only Wins, Can't have the second dataset
    if len(objective_data) == 1:

        win = 'Wins' if objective_data[0]['Win'] else 'Losses'

        graph_info = {
        # Autoscales, 0-6
        'objective_graph': {
            'labels': [
                {'text': 'Barons Killed'},
                {'text': 'Void Grubs Killed'},
                {'text': 'Dragons Killed'},
                {'text': 'Turrets Destroyed'},
                {'text': 'Turret Plates Taken'},
                {'text': 'Rift Heralds Killed'}
                
            ],
            'datasets':[
                {
                    'label': win,
                    'data': [objective_data[0]['Barons_Killed'], 
                             objective_data[0]['Void_Grubs_Killed'], 
                             objective_data[0]['Dragons_Killed'], 
                             objective_data[0]['Turrets_Killed'],
                             effectiveness_data[0]['Turret_Plates_Taken'],
                             objective_data[0]['Rift_Heralds_Killed']]
                }
            ]
        }, 
        # Autoscale Should Work, Between 0 - 150 ish
        'resource_graph': {
            'labels': [
                {'text': 'Normalized Gold Per Minute in Tens'},
                {'text': 'Total Minions Killed'},
                {'text': 'Total Jungle Monsters Killed'},
                {'text': 'Lane CS Before 10 Minutes'},
                {'text': 'Jungle CS Before 10 Minutes'}

            ],
            'datasets':[
                {
                    'label': win,
                    'data': [effectiveness_data[0]['Gold_Per_Minute'] / 10, 
                             effectiveness_data[0]['Total_Minions_Killed'], 
                             effectiveness_data[0]['Total_Jungle_Monsters_Killed'], 
                             effectiveness_data[0]['Lane_Minions_Before_10_Minutes'], 
                             effectiveness_data[0]['Jungle_CS_Before_10_Minutes']]
                }
            ]
        }, 
        # Autoscaled, Between 0 - 10 usually
        'combat_graph': {
            'labels': [
                {'text': 'Total Damage Dealt To Champions In Ten Thousands'},
                {'text': 'KDA'},
                {'text': 'Damage Per Minute In Hundreds'},
                {'text': 'Team Damage Share'},
                {'text': 'Kill Participation'},
                {'text': 'Vision Score Per Minute'},
                {'text': 'Solo Kills'}
            ],
            'datasets':[
                
                {
                    'label': win,
                    'data': [effectiveness_data[0]['Total_Damage_DealtToChampions'] / 10000, 
                             effectiveness_data[0]['KDA'], 
                             effectiveness_data[0]['Damage_Per_Minute'] / 100,
                             effectiveness_data[0]['Damage_Share'], 
                             effectiveness_data[0]['Kill_Participation'], 
                             effectiveness_data[0]['Vision_Score_Per_Minute'],
                             effectiveness_data[0]['Sol_Kills']]
                            
                }
            ]
        }, 
    }
    
    else:

        graph_info = {
            # Autoscales, 0-6
            'objective_graph': {
                'labels': [
                    {'text': 'Barons Killed'},
                    {'text': 'Void Grubs Killed'},
                    {'text': 'Dragons Killed'},
                    {'text': 'Turrets Destroyed'},
                    {'text': 'Turret Plates Taken'},
                    {'text': 'Rift Heralds Killed'}
                    
                ],
                'datasets':[
                    
                
                    { 
                        'label': 'Wins',
                        'data': [objective_data[1]['Barons_Killed'], 
                                objective_data[1]['Void_Grubs_Killed'], 
                                objective_data[1]['Dragons_Killed'], 
                                objective_data[1]['Turrets_Killed'], 
                                effectiveness_data[1]['Turret_Plates_Taken'],
                                objective_data[1]['Rift_Heralds_Killed']]
                    },
                    {
                        'label': 'Losses',
                        'data': [objective_data[0]['Barons_Killed'], 
                                objective_data[0]['Void_Grubs_Killed'], 
                                objective_data[0]['Dragons_Killed'], 
                                objective_data[0]['Turrets_Killed'],
                                effectiveness_data[0]['Turret_Plates_Taken'],
                                objective_data[0]['Rift_Heralds_Killed']]
                    }
                ]
            }, 
            # Autoscale Should Work, Between 0 - 150 ish
            'resource_graph': {
                'labels': [
                    {'text': 'Normalized Gold Per Minute in Tens'},
                    {'text': 'Total Minions Killed'},
                    {'text': 'Total Jungle Monsters Killed'},
                    {'text': 'Lane CS Before 10 Minutes'},
                    {'text': 'Jungle CS Before 10 Minutes'}

                ],
                'datasets':[
                    
                
                    { 
                        'label': 'Wins',
                        'data': [effectiveness_data[1]['Gold_Per_Minute'] / 10, 
                                effectiveness_data[1]['Total_Minions_Killed'], 
                                effectiveness_data[1]['Total_Jungle_Monsters_Killed'], 
                                effectiveness_data[1]['Lane_Minions_Before_10_Minutes'], 
                                effectiveness_data[1]['Jungle_CS_Before_10_Minutes']]
                                

                    },
                    {
                        'label': 'Losses',
                        'data': [effectiveness_data[0]['Gold_Per_Minute'] / 10, 
                                effectiveness_data[0]['Total_Minions_Killed'], 
                                effectiveness_data[0]['Total_Jungle_Monsters_Killed'], 
                                effectiveness_data[0]['Lane_Minions_Before_10_Minutes'], 
                                effectiveness_data[0]['Jungle_CS_Before_10_Minutes']]
                    }
                ]
            }, 
            # Autoscaled, Between 0 - 10 usually
            'combat_graph': {
                'labels': [
                    {'text': 'Total Damage Dealt To Champions In Ten Thousands'},
                    {'text': 'KDA'},
                    {'text': 'Damage Per Minute In Hundreds'},
                    {'text': 'Team Damage Share'},
                    {'text': 'Kill Participation'},
                    {'text': 'Vision Score Per Minute'},
                    {'text': 'Solo Kills'}
                ],
                'datasets':[
                    
                
                    { 
                        'label': 'Wins',
                        'data': [effectiveness_data[1]['Total_Damage_DealtToChampions'] / 10000, 
                                effectiveness_data[1]['KDA'], 
                                effectiveness_data[1]['Damage_Per_Minute'] / 100,
                                effectiveness_data[1]['Damage_Share'], 
                                effectiveness_data[1]['Kill_Participation'], 
                                effectiveness_data[1]['Vision_Score_Per_Minute'],
                                effectiveness_data[1]['Sol_Kills']]
                                

                    },
                    {
                        'label': 'Losses',
                        'data': [effectiveness_data[0]['Total_Damage_DealtToChampions'] / 10000, 
                                effectiveness_data[0]['KDA'], 
                                effectiveness_data[0]['Damage_Per_Minute'] / 100,
                                effectiveness_data[0]['Damage_Share'], 
                                effectiveness_data[0]['Kill_Participation'], 
                                effectiveness_data[0]['Vision_Score_Per_Minute'],
                                effectiveness_data[0]['Sol_Kills']]
                                
                    }
                ]
            }, 
        }

    return graph_info

"""
Best Runepages Logic and Retrieval
"""

def get_runepage_recs(raw_data: dict) -> dict:

    runepage_data = raw_data['keystone_runes_data']
    # Find the runepages with the best winrate, best score (games played * winrate), and most games played
    best_runepages = [max(runepage_data, key=lambda x: x['Winrate']), 
                     max(runepage_data, key=lambda x: x['Score']), 
                     max(runepage_data, key=lambda x: x['Games_Played'])]
    
    
    # Sort this into a dictionary to be passed to the frontend
    runepage_info = {
        'winrate_keystone': best_runepages[0]['Primary_Keystone'],
        'winrate_secondary': best_runepages[0]['Secondary_Tree'],
        'winrate_wr': best_runepages[0]['Winrate'],
        'winrate_gp': best_runepages[0]['Games_Played'],
        'score_keystone': best_runepages[1]['Primary_Keystone'],
        'score_secondary': best_runepages[1]['Secondary_Tree'],
        'score_wr': best_runepages[1]['Winrate'],
        'score_gp': best_runepages[1]['Games_Played'],
        'games_keystone': best_runepages[2]['Primary_Keystone'],
        'games_secondary': best_runepages[2]['Secondary_Tree'],
        'games_wr': best_runepages[2]['Winrate'],
        'games_gp': best_runepages[2]['Games_Played'],
    }

    return runepage_info



"""
Image Retrieval
"""
def get_images_from_folder(folder_path: str):
    """
    Retrieves all .png files from a specified path
    """
    try:
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        return image_files
    except Exception as e:
        return {'error': str(e)}



@app.route('/images/<path:filename>')
def serve_image(filename: str):
    return send_from_directory('static/images', filename)



@app.route('/api/images')
def get_images():
    """
    Provides images to frontend from a specified folder
    """
    folder = request.args.get('folder', 'general/poro')
    image_folder = os.path.join('static/images', folder)
    image_files = get_images_from_folder(image_folder)
    if 'error' in image_files:
        return jsonify({'error': image_files['error']}), 500
    return jsonify(image_files)

"""
Data Retrieval/Update
"""
@app.route('/api/search', methods=['POST'])
def search():
    """
    Checks if the input from the search bar contains valid information, if so, provides a redirect url for a script to handle
    If the data doesn't exist, returns exists as false, which a script will handle and provide a pop-up error message
    """
    data = request.get_json()

    name_change = {
        'Lee Sin': 'LeeSin',
        'Jarvan IV': 'JarvanIV',
        'Aurelion Sol': 'AurelionSol',
        'Miss Fortune': 'MissFortune',
        'Master Yi': 'MasterYi',
        'Tahm Kench': 'TahmKench',
        'Xin Zhao': 'XinZhao',
        'Twisted Fate': 'TwistedFate',
        'Dr Mundo': 'DrMundo'
    }
    champion_name = name_change[data['championName']] if data['championName'] in name_change else data['championName']

    info = get_champion_data(champion_name, data['role'])
    exists = any(info.values())

    if exists and info['winrate_data']:
        redirect_url = url_for('champion_page', champion=data['championName'], role=data['role'])
        return jsonify({'exists': True, 'redirect_url': redirect_url})
    else:
        return jsonify({'exists': False})
    

"""
Template Rendering
"""
@app.route('/')
def home():
    """
    Routes to homepage index.html
    """
    return render_template('index.html')



@app.route('/champion')
def champion_page():
    """
    Routes to champion.html, inputing the champion, role, and the data associated with those two values
    """

    
    champion = request.args.get('champion')
    
    role = request.args.get('role')

    external_champion = champion
    name_change = {
        'Lee Sin': 'LeeSin',
        'Jarvan IV': 'JarvanIV',
        'Aurelion Sol': 'AurelionSol',
        'Miss Fortune': 'MissFortune',
        'Master Yi': 'MasterYi',
        'Tahm Kench': 'TahmKench',
        'Xin Zhao': 'XinZhao',
        'Twisted Fate': 'TwistedFate',
        'Dr Mundo': 'DrMundo'
    }

    champion = name_change[external_champion] if external_champion in name_change else champion

    
    

    raw_info = get_champion_data(champion, role)

    role_map = {
        'TOP': 'Top',
        'JUNGLE': 'Jungle',
        'MIDDLE': 'Middle',
        'BOTTOM': 'Bottom',
        'UTILITY': 'Support'
    }
    external_role = role_map[role]

    radar_labels = get_radar_graph_labels(raw_data=raw_info)
    item_table_info = raw_info['item_winrate_data']

    runepage_info = get_runepage_recs(raw_data = raw_info)
    

    return render_template('champion.html', champion=champion, role=role, info=raw_info, radar_graph_info = radar_labels, 
                           external_role = external_role, item_table_info = item_table_info, runepage_info = runepage_info
                           , external_champion=external_champion)



if __name__ == '__main__':
    app.run(debug=True)































