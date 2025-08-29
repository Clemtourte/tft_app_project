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