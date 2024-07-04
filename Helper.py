import requests
import time
import json

def fetch_account_puuid(gameName: str, tagLine: str, api_key: str, region = "americas") -> dict:
    """

    Fetch a PUUID by Riot ID. 

    @Parameters:
        gameName & tagLine (strs): A Riot ID is comprised of gameName#tagLine. This is how a Riot ID is fed into this method.
        api_key (str): Riot API key.
        region (str): The region for which we are looking for the player with the corresponding RiotID.

    @Return:
        str: The Corresponding User's PUUID.

    """

    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    
    headers = {
        'X-Riot-Token': api_key
    }

    resp = requests.get(url, headers = headers)
    
    if resp.status_code == 200:
        return resp.json()["puuid"]
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
        list: A list of match IDs.    

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

    resp = requests.get(url, headers= headers, params= parameters)

    if resp.status_code == 200:
        return resp.json()
    else:
        raise ValueError(f'Error: {resp.status_code}, {resp.json()["status"]["message"]}')




def fetch_all_matches(puuid: str, api_key:str, region = "americas", batch_size = 100, startTime = None, delay = 1.2) -> list:
    """

    Fetches all match IDs for a given PUUID.
    
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
        matches = fetch_match_batch(puuid = puuid, start = start_idx, count = batch_size, api_key = api_key, startTime = startTime)
        if not matches:
            break
        res_matches.extend(matches)
        start_idx += batch_size

        if len(matches) < batch_size:
            break
            
        time.sleep(delay)

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
    
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        latest_match = resp.json()
    else:
        raise ValueError(f'Error: {resp.status_code}, {resp.json()['status']['message']}')
        
    timestamp = latest_match['info']['gameCreation']

    res_dict = {
        'latest': timestamp,
        'matchlist': matchlist
    } 

    to_json = json.dumps(res_dict, indent = 4)
    
    with open(filename, "w") as json_file:
        json_file.write(to_json)




def json_to_matches(filename = "matches.json") -> tuple:
    """

    Reads the file and converts it to a list of matches and the timestamp of the latest match

    @Parameters:
        filename (str): The .json file the dictionary of the matchlist is stored in.
         
    @Returns:
        tuple, a list of all matches and the timestamp of the latest match

    """

    with open(filename, 'r') as file:
        data = json.load(file)
    
    if not data['latest'] or not data['matchlist']:
        raise ValueError("JSON file not properly formatted.")

    return data['latest'], data['matchlist']






def update_matches(puuid: str, startTime: int, start: int, count: int, api_key: str, region = "americas"):
    NotImplemented


def fetch_match_details(match_id: str, api_key: str, puuid: str, region="americas"):
    """
    Fetches details of a specific match by match ID.

    Parameters:
        match_id (str): The ID of the match.
        api_key (str): Riot API key.
        region (str): The region to fetch match details from (default is "americas").

    Returns:
        dict: Details of the match.
    """