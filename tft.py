import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

TRAIT_MAPPING = {
    'ElTigre': 'The Champ',
    'GemForce': 'Crystal Gambit',
    'SentaiRanger': 'Mighty Mech',
    'Spellslinger': 'Sorcerer',
    'OldMentor': 'Mentor',
    'Empyrean': 'Wraith',
    'DragonFist': 'Stance Master',
    'Destroyer': 'Executioner',
    'StarGuardian': 'Star Guardian',
    'SoulFighter': 'Soul Fighter',
    'TheCrew': 'The Crew',
    'BattleAcademia': 'Battle Academia',
    'SupremeCells': 'Supreme Cells',
    'ReddBuff': 'Sunfire Cape'
}

ITEM_MAPPING = {
    'MadredsBloodrazor': 'Giant Slayer',
    'PowerGauntlet': 'Striker\'s Flail',
    'RunaansHurricane': 'Kraken\'s Fury',
    'SpectralGauntlet' : 'Evenshroud',
    'StatikkShiv' : 'Void Staff',
    'RapidFireCannon': 'Red Buff',
    'GuardianAngel': 'Edge of Night',
    'FrozenHeart': 'Protector\'s Vow',
    'Redemption': 'Spirit Visage',
    'UnstableConcoction': 'Hand of Justice',
    'NightHarvester': 'Steadfast Heart',
    'Leviathan': 'Nashor\'s Tooth',
    'Artifact': 'Blighting Jewel'
}

GAMETYPE_MAPPING = {
    'standard' : 'Ranked',
    'pairs' : 'Double Up'
}

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
username = 'Tourtipouss'
tag = '9861'

puuid = get_puuid(username, tag, API_KEY)

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

match_ids = get_matchid(puuid,0, 20, API_KEY)

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

match_data = get_match_info(match_ids,API_KEY)

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

CHAMPION_COSTS = get_champion_cost()

def get_character_info(match_data, match_indices=None):
    if match_indices is None:
        match_indices = range(len(match_data))
    
    for match_index in match_indices:
        mapped_game_type = GAMETYPE_MAPPING.get(match_data[match_index]['info']['tft_game_type'],match_data[match_index]['info']['tft_game_type'])
        print(f"=== MATCH {match_index+1} {mapped_game_type} ===")
        sorted_participants = sorted(match_data[match_index]['info']['participants'], key=lambda p: p['placement'])
        for participant in sorted_participants:
            total_board_value = sum(CHAMPION_COSTS.get(unit['character_id'].split('_')[1], 0) for unit in participant['units'])
            print(f'{participant['placement']}_{participant['riotIdGameName']} ({participant['total_damage_to_players']} damage to players):\nCharacters (Total board value: {total_board_value}):')
            for unit in participant['units']:
                clean_name = unit['character_id'].split('_')[1]
                clean_items = [item.split('_')[2] for item in unit['itemNames']]
                mapped_items = [ITEM_MAPPING.get(item, item) for item in clean_items]
                items_str = f" ({', '.join(mapped_items)})" if mapped_items else " (no items)"
                print(f'{clean_name}{items_str}')
            print()
            print('Traits:')
            for trait in participant['traits']:
                clean_trait = trait['name'].split('_')[1]
                mapped_trait = TRAIT_MAPPING.get(clean_trait, clean_trait)
                num_units = trait['num_units']
                if trait['tier_current'] > 0 :
                        print(f'{num_units} {mapped_trait}')
            print()
        print("\n" + "="*50 + "\n")

get_character_info(match_data)
