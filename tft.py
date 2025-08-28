import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')

username = 'Tourtipouss'
tag = '9861'

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

def calculate_board_value(units):
    return sum(CHAMPION_COSTS.get(unit['character_id'].split('_')[1], 0) for unit in units)

def get_champion_name(unit):
    return unit['character_id'].split('_')[1]

def format_unit_info(unit):
    clean_name = get_champion_name(unit)
    clean_items = [item.split('_')[2] for item in unit['itemNames']]
    mapped_items = [ITEM_MAPPING.get(item, item) for item in clean_items]
    items_str = f" ({', '.join(mapped_items)})" if mapped_items else " (no items)"
    return f'{clean_name}{items_str}'

def format_traits_info(traits):
    active_traits = []
    for trait in traits:
        if trait['tier_current'] > 0:
            clean_trait = trait['name'].split('_')[1]
            mapped_trait = TRAIT_MAPPING.get(clean_trait, clean_trait)
            num_units = trait['num_units']
            active_traits.append(f'{num_units} {mapped_trait}')
    return active_traits

def format_participant_info(participant):
    placement = participant['placement']
    riot_id_game_name = participant['riotIdGameName']
    total_damage = participant['total_damage_to_players']
    board_value = calculate_board_value(participant['units'])
    
    participant_text = f'{placement}_{riot_id_game_name} ({total_damage} damage to players):\n'
    participant_text += f'Characters (Total board value: {board_value}):\n'
    
    for unit in participant['units']:
        participant_text += format_unit_info(unit) + '\n'
    
    participant_text += '\nTraits:\n'
    
    active_traits = format_traits_info(participant['traits'])
    for trait in active_traits:
        participant_text += trait + '\n'
    
    return participant_text

def display_single_match(match_info, match_number):
    game_type = match_info['info']['tft_game_type']
    mapped_game_type = GAMETYPE_MAPPING.get(game_type, game_type)
    
    print(f"=== MATCH {match_number} {mapped_game_type} ===")
    
    sorted_participants = sorted(match_info['info']['participants'], key=lambda p: p['placement'])
    
    for participant in sorted_participants:
        participant_info = format_participant_info(participant)
        print(participant_info)
    
    print("\n" + "="*50 + "\n")

def display_matches(match_data, match_indices=None):
    if match_indices is None:
        match_indices = range(len(match_data))
    
    for match_index in match_indices:
        display_single_match(match_data[match_index], match_index + 1)

display_matches(match_data)

def extract_user_matches(match_data, puuid):
    user_matches = []
    for match in match_data:
        for participant in match['info']['participants']:
            if participant['puuid'] == puuid:
                participant_with_game_type = participant.copy()
                participant_with_game_type['game_type'] = match['info']['tft_game_type']
                user_matches.append(participant_with_game_type)
                break
    return user_matches

def display_game_type_stats(filtered_matches, display_name):
    if filtered_matches:
        placements = [match['placement'] for match in filtered_matches]
        avg_placement = sum(placements) / len(placements)
        print(f'{display_name} average: {round(avg_placement, 2)} ({len(filtered_matches)} matches)')
        print(f'{display_name} placements: {placements}')

def display_user_stats(match_data, puuid):
    user_matches = extract_user_matches(match_data, puuid)
    if not user_matches:
        print('No matches found for this player')
        return
    
    username = user_matches[0]['riotIdGameName']
    placements = [match['placement'] for match in user_matches]
    avg_placement = sum(placements)/len(placements)

    print(f'{username} average placement: {round(avg_placement, 2)} (Number of matches: {len(user_matches)})')
    print(f'Placements: {placements}')

    ranked_matches = [m for m in user_matches if m['game_type'] == 'standard']
    display_game_type_stats(ranked_matches, 'Ranked')

    doubleup_matches = [m for m in user_matches if m['game_type'] == 'pairs']
    display_game_type_stats(doubleup_matches, 'DoubleUp')    

display_user_stats(match_data, puuid)

def display_user_champion_games(match_data, puuid, top_champions):
    champion_count = {}
    user_matches = extract_user_matches(match_data, puuid)

    for match in user_matches:
        for unit in match['units']:
            champion_name = get_champion_name(unit)
            champion_count[champion_name] = champion_count.get(champion_name,0) + 1
    
    sorted_champions = sorted(champion_count.items(),key=lambda x:x[1], reverse=True)
    print(f'Most played champions :')
    for champion, count in sorted_champions[:top_champions]:
        print(f'{champion}: {count} times')

display_user_champion_games(match_data, puuid, 10)

def analyze_champion_perfs(user_matches):
    champion_stats = {}

    for match in user_matches:
        placement = match['placement']
        for unit in match['units']:
            champion_name = get_champion_name(unit)
            if champion_name not in champion_stats:
                champion_stats[champion_name] = {'placements': []}
            
            champion_stats[champion_name]['placements'].append(placement)
    
    for champion, data in champion_stats.items():
        placements = data['placements']
        data['games'] = len(placements)
        data['avg_placement'] = sum(placements)/len(placements)

        data['top4_count'] = sum(1 for p in placements if p <=4)
        data['top4_rate'] = (data['top4_count']/data['games'])*100

        data['win_count'] = sum(1 for p in placements if p ==1)
        data['win_rate'] = (data['win_count']/data['games'])*100
    
    return champion_stats


def display_champion_performance(match_data,puuid):
    user_matches = extract_user_matches(match_data,puuid)
    
    if not user_matches:
        print('No matches found for this player')
        return
    
    champion_stats = analyze_champion_perfs(user_matches)

    if not champion_stats:
        print('No champion stats for this player')
        return
    
    sorted_champions = sorted(champion_stats.items(),
                              key = lambda x: x[1]['games'],
                              reverse= True)
    sorted_champions = [(champ, stats) for champ, stats in sorted_champions 
                   if stats['games'] >= 3]
    print(f'{'Champion':<15} {'Games':<6} {'Avg Place':<10} {'Top 4%':<8} {'Win %':<8}')
    print('-'*55)

    for champion,stats in sorted_champions:
        print(f'{champion:<15} {stats['games']:<6} '
              f'{stats['avg_placement']:<10.2f} '
              f'{stats['top4_rate']:<8.1f}% '
              f'{stats['win_rate']:<8.1f}%')


display_champion_performance(match_data,puuid)