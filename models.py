from db import get_supabase_client

supabase = get_supabase_client()

def add_player(username, tag, puuid):
    try:
        supabase.table('players').upsert({
            'puuid': puuid,
            'username': username,
            'tag': tag
        }).execute()
        print(f'Player {username}#{tag} added')
        return True
    except Exception as e:
        print(f'Error adding player: {e}')
        return False
    
def get_existing_match_ids():
    try:
        result = supabase.table('matches').select('match_id').execute()
        return {match['match_id'] for match in result.data}
    except Exception as e:
        print(f'Error fetching match IDs: {e}')
        return set()
    
def store_match(match_data):
    try:
        match_id = match_data['metadata']['match_id']
        game_type = match_data['info']['tft_game_type']

        supabase.table('matches').upsert({
            'match_id': match_id,
            'raw_data': match_data,
            'game_type': game_type
        }).execute()

        print(f'Match {match_id} stored')
        return match_id
    except Exception as e:
        print(f'Error storing match: {e}')
        return None
    
def get_tracked_players():
    try:
        result = supabase.table('players').select('puuid').execute()
        return {player['puuid'] for player in result.data}
    except Exception as e:
        print(f'Error fetching tracked players: {e}')
        return set()


def store_participant_relations(match_data):
    try:
        match_id = match_data['metadata']['match_id']
        participants = match_data['info']['participants']
        tracked_puuids = get_tracked_players()
        
        stored_count = 0
        for participant in participants:
            puuid = participant['puuid']
            placement = participant['placement']

            if puuid in tracked_puuids:
                supabase.table('player_matches').upsert({
                    'puuid': puuid,
                    'match_id': match_id,
                    'placement': placement
                }).execute()
                stored_count +=1
        
        print(f"Stored {len(participants)} participant relations for {match_id}")
        return True
    except Exception as e:
        print(f"Error storing participant relations: {e}")
        return False
