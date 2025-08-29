import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

def get_puuid(username, tag, API_KEY):
    account_url = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id'
    url = f"{account_url}/{username}/{tag}?api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['puuid']
    except requests.RequestException as e:
        print(f"API error: {e}")
        print(f"Status Code: {response.status_code if 'response' in locals() else 'N/A'}")
        return None


def get_matchid(puuid,start,count,API_key):
    matchid_url = 'https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid'
    url = f"{matchid_url}/{puuid}/ids?start={start}&count={count}&api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"API error: {e}")
        print(f"Status Code: {response.status_code if 'response' in locals() else 'N/A'}")
        return None


def get_match_info(match_ids, API_KEY):
    matchinfo_url = 'https://europe.api.riotgames.com/tft/match/v1/matches'
    match_info = []
    for match_id in match_ids:
        url = f"{matchinfo_url}/{match_id}?api_key={API_KEY}"
        try:             
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            match_info.append(data)
        except requests.RequestException as e:
            print(f"API error: {e}")
            print(f"Status Code: {response.status_code if 'response' in locals() else 'N/A'}")
            return None
    return match_info


def get_champion_cost():
    response = requests.get('https://ddragon.leagueoflegends.com/cdn/15.17.1/data/en_US/tft-champion.json')
    ddragon = response.json()

    champions_cost = {}
    for champion_id, champion_data in ddragon['data'].items():
        if 'TFT15_' in champion_id:
            clean_name = champion_id.split('_')[1]
            cost =  champion_data['tier']
            champions_cost[clean_name] = cost
    return champions_cost
