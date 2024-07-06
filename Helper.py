import requests
import time
import json
import logging

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

    