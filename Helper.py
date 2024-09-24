import os
import pathlib
import re
import requests
import time
import json
import logging
import pandas as pd
from pandas import DataFrame

latest_patch = '14.14.1'

def handle_rate_limit(resp):
    """

    Handles the case in which the Rate Limit (100/2mins, 20/1s) is Exceeded, sleeps the program if the limit is exceeded.

    @Parameters:
        resp (Response): Response from Request made.
    
    @Returns:
        Return True if the rate limit was exceeded and the program was slept, false otherwise.

    """
    if resp.status_code == 429:
        retry_after = int(resp.headers.get('Retry-After', 10))
        logging.warning(f"Rate limit hit. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)
        return True
    return False



def fetch_account_puuid(gameName: str, tagLine: str, api_key: str, region = "americas") -> dict:
    """

    Fetch a PUUID by Riot ID. 

    @Parameters:
        gameName & tagLine (strs): A Riot ID is comprised of gameName#tagLine. This is how a Riot ID is fed into this method.
        api_key (str): Riot API key.
        region (str): The region for which we are looking for the player with the corresponding RiotID.

    @Return:
        str: The Corresponding User's PUUID. Returns -1 if Rate Limit exceeded

    """

    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    
    headers = {
        'X-Riot-Token': api_key
    }

    while True:
        resp = requests.get(url, headers = headers)
        
        if resp.status_code == 200:
            return resp.json()["puuid"]
        elif handle_rate_limit(resp):
            continue
        else:
            raise ValueError(f'Error: {resp.status_code}, {resp.json()["status"]["message"]}')



def fetch_match_batch(puuid: str, start: int, count: int, api_key: str, startTime = None, region = "americas") -> list:
    """

    Fetches a batch of match IDs for a given PUUID.
    
    @Parameters:
        puuid (str): The PUUID of the summoner.
        start (int): The start index for fetching matches.
        count (int): The number of matches to fetch.
        api_key (str): Riot API key.
        startTime (int, optional): The start time to fetch matches from.
        region (str): The region to fetch matches from.
    
    @Returns:
        list: A list of match IDs. Returns -1 if rate limit exceeded

    """
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    
    headers = {
        'X-Riot-Token': api_key
    }


    parameters = {
        "start": start,
        "count": count
    }

    if startTime:
        parameters["startTime"] = startTime

    while True:
        resp = requests.get(url, headers= headers, params= parameters)

        if resp.status_code == 200:
            return resp.json()
        elif handle_rate_limit(resp):
            continue
        else:
            raise ValueError(f'Error: {resp.status_code}, {resp.json()["status"]["message"]}')



def fetch_all_matches(puuid: str, api_key:str, region = "americas", batch_size = 100, startTime = None) -> list:
    """

    Fetches all match IDs for a given PUUID. Note: Riot only stores the past 990 matches. Call this method ONLY when fetching the initial batch,
    see update_matches() to update the list with the most recent matches without deleting the oldest matches.
    
    @Parameters:
        puuid (str): The PUUID of the summoner.
        api_key (str): Riot API key.
        region (str): The region to fetch matches from.
        batch_size (int, optional): The number of mathces to fetch per request. 
        startTime (int, optional): The timestamp for which we start fetching matches
        delay (float): Delay between requests in respect to the rate limit (120s/100reqs)
    
    @Returns:
        list: A list of match IDs throughout the summoner's lifetime    

    """

    start_idx = 0
    res_matches = []

    while True:
        matches = fetch_match_batch(puuid = puuid, start = start_idx, count = batch_size, api_key = api_key, startTime = startTime, region = region)
        
        if not matches:
            break
        res_matches.extend(matches)
        start_idx += batch_size

        #if len(matches) < batch_size:
        #    break
            

    return res_matches



def matches_to_json(matchlist: list[str], api_key: str, filename = "matches.json", region = "americas") -> None:
    """

    Stores matchlist into a json file as a dictionary under key 'matchlist', and the timestamp of the most recent match in 'latest'

    @Parameters:
        api_key (str): Riot API key.
        region (str): The region to fetch matches from.
        filename (str): The .json file for the dictionary to be stored in.
        matchlist (list[str]): A list of the match IDs to be stored.   
         
    @Returns:
        None, creates a new File   

    """

    most_recent = matchlist[0]

    headers = {
        'X-Riot-Token': api_key
    }

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{most_recent}"
    
    while True:
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            latest_match = resp.json()
            break
        elif handle_rate_limit(resp):
            continue
        else:
            raise ValueError(f'Error: {resp.status_code}, {resp.json()['status']['message']}')
        
    timestamp = latest_match['info']['gameCreation'] // 1000 # Calculate the timestamp of the start of the most recent game

    res_dict = {
        'latest': timestamp,
        'matchlist': matchlist
    } 

    
    with open(filename, "w") as json_file:
        json.dump(res_dict, json_file, indent=4)



def json_to_matches(filename = "matches.json") -> tuple:
    """

    Reads the file and converts it to a list of matches and the timestamp of the latest match, plus the index of the last match that has been processed

    @Parameters:
        filename (str): The .json file the dictionary of the matchlist is stored in.
         
    @Returns:
        tuple, a list of all matches, the timestamp of the latest match, and the index of the last processed match

    """

    with open(filename, 'r') as file:
        data = json.load(file)
    
    if 'latest' not in data or 'matchlist' not in data:
        raise ValueError("JSON file not properly formatted.")

    return data['latest'], data['matchlist']



def update_matches(puuid: str, api_key: str, filename = "matches.json") -> None:
    """

    Fetches and adds the most recent matches to matches.json, updates the matchlist and latest keys

    @Parameters:
        api_key (str): Riot API key.
        filename (str): The .json file for the dictionary to be stored in.
        puuid (str): The puuid of the User

    @Returns:
        None, Updates filename
    """
    latest_timestamp, matchlist = json_to_matches(filename)

    new_matches = fetch_all_matches(puuid=puuid, api_key = api_key, startTime = latest_timestamp)[:-1]
    temp = len(new_matches)
    new_matches.extend(matchlist)

    matches_to_json(matchlist = new_matches, api_key = api_key, filename = "matches.json")
    return temp



def fetch_match_details(match_id: str, api_key: str, region = "americas") -> dict:
    """
    Fetches details of a specific match by match ID.

    @Parameters:
        match_id (str): The ID of the match.
        api_key (str): Riot API key.
        region (str): The region to fetch match details from.

    Returns:
        dict: Details of the match.
    """

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"

    headers = {
        'X-Riot-Token': api_key
    }

    while True:
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            return resp.json()
        elif handle_rate_limit(resp):
            continue
        else:
            raise ValueError(f'Error: {resp.status_code}, {resp.json()['status']['message']}')

    

def fetch_match_timeline(match_id: str, api_key: str, region="americas") -> dict:
    
    """
    Fetches the match timeline match by match ID.

    Parameters:
        match_id (str): The ID of the match.
        api_key (str): Riot API key.
        region (str): The region to fetch match details from.

    @Returns:
        dict: Details of the match as a timeline.
    """

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"

    headers = {
        'X-Riot-Token': api_key
    }

    while True:
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            return resp.json()
        elif handle_rate_limit(resp):
            continue
        else:
            raise ValueError(f'Error: {resp.status_code}, {resp.json()['status']['message']}')


    
def process_match_details(match: json, puuid: str, filterMap = 11) -> DataFrame:
    """
    Processes Match Details and Statistics of a player and stores relevant Information into a Dataframe. To See what information is processed, see matchInfo.txt

    @Parameters:
        match (json): The json of the match, retrieved using fetch_match_details() method
        puuid (str): The player for which we are fetching statistics for
        filterMap (int): The type of map for which we are to process. If the mapId doesn't match, then skip

    @Return:
        A DataFrame with all relevant data
    """
    match_info = match['info']

    # Check mapID
    mapID = match_info.get('mapId')
    if filterMap and filterMap != mapID: 
        return None

    # Fetch the index of the participant
    idx = match['metadata']['participants'].index(puuid) 

    # Fetch All Information
    patch_nums = str(match_info.get('gameVersion', '')).split('.')
    patch = ".".join(patch_nums[:2])

    # Fetch Dictionaries of General Categories
    player_info = match_info['participants'][idx]
    challenges = player_info.get('challenges', {})
    perks = player_info.get('perks', {})
    stat_runes = perks.get('statPerks', {})
    primary_runes = perks.get('styles', [{}])[0]
    secondary_runes = perks.get('styles', [{}, {}])[1]

    # Determine the teamID and which team the player is playing on
    teamID = player_info.get('teamId')
    team = None
    for t in match_info.get('teams', []):
        if t.get('teamId') == teamID:
            team = t
            break

    objectives = team.get('objectives', {}) if team else {}

    # Fetch Individual Relevant Statistics

    # General Information
    champion = player_info.get('championName')
    role = player_info.get('teamPosition')
    win = player_info.get('win')
    summoner_1 = player_info.get('summoner1Id')
    summoner_2 = player_info.get('summoner2Id')

    # General Statistics/Info
    turrets_killed = player_info.get('turretTakedowns')
    totalMinionsKilled = player_info.get('totalMinionsKilled')
    totalJungleKilled = player_info.get('totalAllyJungleMinionsKilled', 0) + player_info.get('totalEnemyJungleMinionsKilled', 0)
    totalDamage = player_info.get('totalDamageDealtToChampions')
    item0 = player_info.get('item0')
    item1 = player_info.get('item1')
    item2 = player_info.get('item2')
    item3 = player_info.get('item3')
    item4 = player_info.get('item4')
    item5 = player_info.get('item5')
    item6 = player_info.get('item6')
    
    # Statistics in Challenges
    kda = challenges.get('kda')
    kill_participation = challenges.get('killParticipation')
    damage_share = challenges.get('teamDamagePercentage')
    turret_plates = challenges.get('turretPlatesTaken')
    gold_pm = challenges.get('goldPerMinute')
    damage_pm = challenges.get('damagePerMinute')
    vision_score_pm = challenges.get('visionScorePerMinute')
    cs_after_10 = challenges.get('laneMinionsFirst10Minutes')
    jungle_after_10 = challenges.get('jungleCsBefore10Minutes')
    solos = challenges.get('soloKills')

    # Map Objective Control in River
    barons = objectives.get('baron', {}).get('kills')
    dragons = objectives.get('dragon', {}).get('kills')
    horde = objectives.get('horde', {}).get('kills')
    heralds = objectives.get('riftHerald', {}).get('kills')

    # Runes
    defense_rune = stat_runes.get('defense')
    flex_rune = stat_runes.get('flex')
    offense_rune = stat_runes.get('offense')

    primary_tree = primary_runes.get('style')
    primary_selections = primary_runes.get('selections', [])
    primary_keystone = primary_selections[0].get('perk') if len(primary_selections) > 0 else None
    primary_choice1 = primary_selections[1].get('perk') if len(primary_selections) > 1 else None
    primary_choice2 = primary_selections[2].get('perk') if len(primary_selections) > 2 else None
    primary_choice3 = primary_selections[3].get('perk') if len(primary_selections) > 3 else None

    secondary_tree = secondary_runes.get('style')
    secondary_selections = secondary_runes.get('selections', [])
    secondary_choice1 = secondary_selections[0].get('perk') if len(secondary_selections) > 0 else None
    secondary_choice2 = secondary_selections[1].get('perk') if len(secondary_selections) > 1 else None


    data_dict = {
        'Champion': [champion],
        'Role': [role],
        'Patch': [patch],
        'Win': [win],
        'Summoner1': [summoner_1],
        'Summoner2': [summoner_2],
        'Turrets_Killed': [turrets_killed],
        'Total_Minions_Killed': [totalMinionsKilled],
        'Total_Jungle_Monsters_Killed': [totalJungleKilled],
        'Total_Damage_DealtToChampions': [totalDamage],
        'Item0': [item0],
        'Item1': [item1],
        'Item2': [item2],
        'Item3': [item3],
        'Item4': [item4],
        'Item5': [item5],
        'Item6': [item6],
        'KDA': [kda],
        'Kill_Participation': [kill_participation],
        'Damage_Share': [damage_share],
        'Turret_Plates_Taken': [turret_plates],
        'Gold_Per_Minute': [gold_pm],
        'Damage_Per_Minute': [damage_pm],
        'Vision_Score_Per_Minute': [vision_score_pm],
        'Lane_Minions_Before_10_Minutes': [cs_after_10],
        'Jungle_CS_Before_10_Minutes': [jungle_after_10],
        'Sol_Kills': [solos],
        'Barons_Killed': [barons],
        'Dragons_Killed': [dragons],
        "Void_Grubs_Killed": [horde],
        'Rift_Heralds_Killed': [heralds],
        'Defense_Rune': [defense_rune],
        'Flex_Rune': [flex_rune],
        'Offense_Rune': [offense_rune],
        'Primary_Tree': [primary_tree],
        'Primary_Keystone': [primary_keystone],
        'Primary_Choice1': [primary_choice1],
        'Primary_Choice2': [primary_choice2],
        'Primary_Choice3': [primary_choice3],
        'Secondary_Tree': [secondary_tree],
        'Secondary_Choice1': [secondary_choice1],
        'Secondary_Choice2': [secondary_choice2]
    }

    return pd.DataFrame(data_dict)



def update_data(puuid: str, api_key: str, datafile = 'data.pkl', matches_file = 'matches.json', new = False) -> None:
    """

    Updates the Dataframe of all of the SR matches

    @Parameters:
        datafile (str): The name of the file for which to load/store the DataFrame object
        matches_file (str): The name of the JSON file of the matchlist
        puuid (str): The PUUID of the player for which we are looking at our data
        api_key (str): The Riot API Key
        new (bool): Set this flag to True if making a new DataFrame, False otherwise
    
    @Return:
        None, Updates datafile with the matches


    """

    # UPDATE MATCHES
    num_new_matches = update_matches(puuid, api_key)
    print(num_new_matches)

    # FETCH MATCH LIST
    _, matchlist = json_to_matches(matches_file)
    
    if num_new_matches == 0 and not new:
        print("No New Matches")
        return 
    
    if new:
        data = pd.DataFrame()
        num_new_matches = len(matchlist)
    else:
        data = pd.read_pickle(datafile)
    

    # PARSE THROUGH NEW MATCHES AND UPDATE DATA
    try:
        # PARSE THROUGH NEW MATCHES AND UPDATE DATA
        for i in range(num_new_matches - 1, -1, -1):
            print("New Match, " + matchlist[i])
            match_json = fetch_match_details(match_id=matchlist[i], api_key=api_key)
            matchDF = process_match_details(match=match_json, puuid=puuid)
            if matchDF is not None and not matchDF.empty:
                data = pd.concat([matchDF, data])
    except Exception as e:
        print(f"Error encountered: {e}") 
        # Server Disconnects/Inconsisitencies with Riot API
    finally:
        data.to_pickle(datafile)
        matches_to_json(matchlist=matchlist, api_key=api_key)



def json_extract_runes(url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json") -> list:
    """
    Returns a dictionary of the rune ID to the rune name

    @Parameters:
        url (str): The url to the json for which we are looking through which has the raw data on the runes, found at communitydragon.org
        

    @Return:
        A dictionary of mappings for {Rune ID: Rune Name}
    
    
    """


    def extract(obj, res, key): # Helper method to extract all values associated with
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    res.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, res, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, res, key)
        return res
    
    item_json = requests.get(url).json()

    ids = extract(item_json, [], 'id')
    names = extract(item_json, [], 'name')
    mydict = dict(map(lambda i, j: (i,j), ids, names))

    return mydict



def json_extract_important_items(url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/items.json") -> list:
    """
    Returns a dictionary of item id to item names of important items that we want to keep track of. The mapping information is provided in a raw json file from communitydragon https://www.communitydragon.org

    @Parameters:
        url (str): The url to the most recent, updated json of the item information of league of legends from community dragon

    @Return:
        A dictionary of mappings of item id to item name
    
    
    """
    
    t2_boots = [3117, 3158, 3047, 3111, 3006, 3005, 3009, 3010, 3020] # ids of tier two boots


    def extract(obj, res, key): # Helper method to extract all values associated with
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    if k in t2_boots or (len(obj["to"]) == 0): # We want tier two boots and objects that don't build into anything else, ie legendary items, starter items, etc. 
                        res.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, res, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, res, key)
        return res

    # Fetch the json from communitydragon
    item_json = requests.get(url).json()

    ids = extract(item_json, [], 'id')
    names = extract(item_json, [], 'name')
    mydict = dict(map(lambda i, j: (i,j), ids, names))

    return mydict



def purge_df(df : DataFrame) -> DataFrame:
    """


    Gets rid of "" and NaN columns in the DataFrame. The Purpose is because Riot API often fills
    columns with these values if the game mechanic isn't in the game yet or the gamemode is different than that of 
    Classic/Ranked SR. Thus, we purge the final DFs to get rid of looking at these classic

    @Parameters
        df (DataFrame): The dataframe for which we are purging the empty string and NaN columns

    @Returns
        a DataFrame of the input df without the rows that feature an empty string or a NaN value

    
    """
    df = df[~df.isin(['']).any(axis=1)]
    df = df.dropna()
    return df



def df_to_statdfs(df : DataFrame) -> tuple:
    
    """
    Takes a dataframe of matches as raw data (unprocessed ids, etc) and turns it into a couple new dataframes, most of them grouping by
    wins and losses, tracking different things like objective control, general stats like kda/gold, item winrates, and rune winrates. 

    @Parameters
        df (DataFrame): The dataframe with the list of matches and their data

    @Returns
        a tuple of DataFrames returned in the following order: 
            objective_df: df that sorts objective control by champion and role
            winrate_by_role: df that calculates winrates based on champion and role
            effectiveness_df: df that displays general statistics like kda, cs, gold, turret plates, vision score, etc.
            tree_runes_df: df that displays winrates of runes by the names of the trees
            keystone_runes_df: df that displays winrates of runes by the name of the keystone, plus the name of the secondary tree
            item_winrate_df: df that displays winrates when building certain legendary items, organized by champion
    
    """
   

 

    # Calculate Objective Control Numbers by Champion, Role, and Win
    objective_df = df.groupby(['Champion', 'Role', 'Win']).agg({
        'Barons_Killed': 'mean',
        'Void_Grubs_Killed': 'mean',
        'Dragons_Killed': 'mean',
        'Turrets_Killed': 'mean',
        'Rift_Heralds_Killed': 'mean',

    }).reset_index()
    objective_df = purge_df(objective_df)
    objective_df = objective_df.round(2)


    # Calculate the Winrates and Games Played By Role
    winrate_by_role = df.groupby(['Champion', 'Role']).agg(
        Winrate=('Win', 'mean'),
        Games_Played=('Win', 'count')
    ).reset_index()
    winrate_by_role = purge_df(winrate_by_role)
    winrate_by_role = winrate_by_role.round(2)

    # Calculate Effectiveness by Wins and Losses
    effectiveness_df = df.groupby(['Champion', 'Role', 'Win']).agg({
            'Total_Minions_Killed': 'mean',
            'Total_Jungle_Monsters_Killed': 'mean',
            'Total_Damage_DealtToChampions': 'mean',
            'KDA': 'mean',
            'Kill_Participation': 'mean',
            'Damage_Share': 'mean',
            'Turret_Plates_Taken': 'mean',
            'Gold_Per_Minute': 'mean',
            'Damage_Per_Minute': 'mean',
            'Vision_Score_Per_Minute': 'mean',
            'Lane_Minions_Before_10_Minutes': 'mean',
            'Jungle_CS_Before_10_Minutes': 'mean',
            'Sol_Kills':'mean'

    }).reset_index()
    effectiveness_df = purge_df(effectiveness_df)
    effectiveness_df = effectiveness_df.round(2)

    # Fetch Runepage ID Matching Dictionaries and Map
    runes = json_extract_runes()
    treepage = {
        8000: "Precision",
        8100: "Domination",
        8200: "Sorcery",
        8300: "Inspiration",
        8400: "Resolve"
    }

    df['Primary_Tree'] = df['Primary_Tree'].replace(treepage)
    df['Secondary_Tree'] = df['Secondary_Tree'].replace(treepage)
    df['Primary_Keystone'] = df['Primary_Keystone'].replace(runes)

    # Calculate Runepages by Tree Winrates
    tree_runes_df = df.groupby(['Champion', 'Role', 'Primary_Tree', 'Secondary_Tree']).agg(
        Winrate=('Win', 'mean'),
        Games_Played=('Win', 'count')
    ).reset_index()
    tree_runes_df = purge_df(tree_runes_df)
    tree_runes_df = tree_runes_df.round(2)


    # Calculate Runepages by Keystone and Secondary Tree Winrates
    keystone_runes_df = df.groupby(['Champion', 'Role', 'Primary_Keystone', 'Secondary_Tree']).agg(
        Winrate=('Win', 'mean'),
        Games_Played=('Win', 'count')
    ).reset_index()
    keystone_runes_df['Score'] = keystone_runes_df['Winrate'] * keystone_runes_df['Games_Played']
    keystone_runes_df = purge_df(keystone_runes_df)
    keystone_runes_df = keystone_runes_df.round(4)
    keystone_runes_df = keystone_runes_df.sort_values(by='Winrate', ascending = False)


    # Calculate Winrates by Item and Champion
    melted_df = df.melt(id_vars=['Champion', 'Win'], value_vars=['Item0', 'Item1', 'Item2', 'Item3', 'Item4', 'Item5', 'Item6'],
                        var_name='ItemSlot', value_name='Item')

    melted_df = melted_df[melted_df['Item'] != 0] # Get rid of empty items

    item_winrate_df = melted_df.groupby(['Champion', 'Item']).agg(
        Winrate=('Win', 'mean'),
        Games_Played=('Win', 'count')
    ).reset_index()

    mydict = json_extract_important_items()

    items_to_keep = list(mydict.keys())
    item_winrate_df = item_winrate_df[item_winrate_df['Item'].isin(items_to_keep)] # Get rid of unwanted items (components, epic items)

    item_winrate_df['Item'] = item_winrate_df['Item'].replace(mydict) # Replace IDs with Names
    item_winrate_df = purge_df(item_winrate_df)
    item_winrate_df = item_winrate_df.round(4)
    item_winrate_df = item_winrate_df.sort_values(by='Games_Played', ascending = False)

    return objective_df, winrate_by_role, effectiveness_df, tree_runes_df, keystone_runes_df, item_winrate_df



def download_item_images(dir = './static/images/items') -> None:
    """
    Downloads images of items that are to be used in the website

    @Parameters:
        url (str): The base url to images by id, found from data dragon

    @Return:
        None, downloads items into the dir folder
    
    
    """
    

    item_dict = json_extract_important_items()

    for id in item_dict:
        name = item_dict[id]
        if re.search(r'[<>:"/\\|?*\n\r]', name):
            continue
        items_url = f'http://ddragon.leagueoflegends.com/cdn/{latest_patch}/img/item/{id}.png'
        save_path = dir + f'/{name}.png'
        
        resp = requests.get(items_url)
        if resp.status_code == 200:
            with open(save_path, 'wb') as file:
                print(f'{name} downloaded')
                file.write(resp.content)



def download_champion_images(dir = './templates/images/champions') -> None:

    """
    Downloads images of champion icons that are to be used in the website

    @Parameters:
        url (str): The base url to images by id, found from data dragon

    @Return:
        None, downloads items into the dir folder
    
    """
    

    
    champions_url = f'http://ddragon.leagueoflegends.com/cdn/{latest_patch}/data/en_US/champion.json'
    resp = requests.get(champions_url)
    data = resp.json()


    for champion in data['data']:
        champ_name = "Wukong" if champion == "MonkeyKing" else champion


        icon_url = f'http://ddragon.leagueoflegends.com/cdn/{latest_patch}/img/champion/{champion}.png'        
        save_path = dir + f'/{champ_name}.png'
        
        resp = requests.get(icon_url)
        if resp.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(resp.content)


