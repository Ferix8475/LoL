import requests
import time
import json
import logging
import pandas as pd
from pandas import DataFrame

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




def matches_to_json(matchlist: list[str], api_key: str, filename = "matches.json", region = "americas", update_ind = 0) -> None:
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
        "last_update": update_ind,
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
    
    if 'last_update' not in data or 'latest' not in data or 'matchlist' not in data:
        raise ValueError("JSON file not properly formatted.")

    return data["last_update"], data['latest'], data['matchlist']




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
    last_ind, latest_timestamp, matchlist = json_to_matches(filename)

    new_matches = fetch_all_matches(puuid=puuid, api_key = api_key, startTime = latest_timestamp)[:-1]
    new_matches.extend(matchlist)

    matches_to_json(matchlist = new_matches, api_key = api_key, filename = "matches.json", update_ind = last_ind)



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
    mapID = match_info['mapId']
    if filterMap and filterMap != mapID: 
        return None

    # Fetch the index of the participant
    idx = match['metadata']['participants'].index(puuid) 

    # Fetch All Information
    patch_nums = str(match_info['gameVersion']).split('.')
    patch = ".".join(patch_nums[:2])

    # Fetch Dictionaries of General Categories
    player_info = match_info['participants'][idx]
    challenges = player_info['challenges']
    perks = player_info['perks']
    stat_runes = perks['statPerks']
    primary_runes = perks['styles'][0]
    secondary_runes = perks['styles'][1]

    # Determine the teamID and which team the player is playing on
    teamID = player_info['teamId']
    for t in match_info['teams']:
        if t['teamId'] == teamID:
            team = t
            break
    objectives = team['objectives']


    # Fetch Individual Relevant Statistics

    # General Information
    champion = player_info['championName']
    role = player_info['teamPosition']
    win = player_info['win']
    summoner_1 = player_info['summoner1Id']
    summoner_2 = player_info['summoner2Id']

    # General Statistics/Info
    turrets_killed = player_info['turretTakedowns']
    totalMinionsKilled = player_info['totalMinionsKilled']
    totalJungleKilled = player_info['totalAllyJungleMinionsKilled'] + player_info['totalEnemyJungleMinionsKilled']
    totalDamage = player_info['totalDamageDealtToChampions']
    item0 = player_info['item0']
    item1 = player_info['item1']
    item2 = player_info['item2']
    item3 = player_info['item3']
    item4 = player_info['item4']
    item5 = player_info['item5']
    item6 = player_info['item6']

    # Statistics in Challenges
    kda = challenges['kda']
    kill_participation = challenges['killParticipation']
    damage_share = challenges['teamDamagePercentage']
    turret_plates = challenges['turretPlatesTaken']
    gold_pm = challenges['goldPerMinute']
    damage_pm = challenges['damagePerMinute']
    takedowns_in_25 = challenges['takedownsFirst25Minutes']
    vision_score_pm =challenges['visionScorePerMinute']
    cs_after_10 =  challenges['laneMinionsFirst10Minutes']
    jungle_after_10 = challenges['jungleCsBefore10Minutes']
    solos = challenges['soloKills']
    turrets_killed = challenges['turretTakedowns']

    # Map Objective Control in River
    barons = objectives['baron']['kills']
    dragons = objectives['dragon']['kills']
    horde = objectives['horde']['kills']
    heralds = objectives['riftHerald']['kills']

    # Runes
    defense_rune = stat_runes['defense']
    flex_rune = stat_runes['flex']
    offense_rune = stat_runes['offense']

    primary_tree = primary_runes['style']
    primary_keystone = primary_runes['selections'][0]['perk']
    primary_choice1 = primary_runes['selections'][1]['perk']
    primary_choice2 = primary_runes['selections'][2]['perk']
    primary_choice3 = primary_runes['selections'][3]['perk']

    secondary_tree = secondary_runes['style']
    secondary_choice1 = secondary_runes['selections'][0]['perk']
    secondary_choice2 = secondary_runes['selections'][1]['perk']


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
        'Takedowns_In_First_25_Minutes': [takedowns_in_25],
        'Vision_Score_Per_Minute': [vision_score_pm],
        'Lane_Minions_Before_10_Minutes': [cs_after_10],
        'Jungle_CS_Before_10_Minutes': [jungle_after_10],
        'Sol_Kills': [solos],
        'Turret_Killed': [turrets_killed],
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




