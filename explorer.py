from models import get_player_matches
from tft import get_champion_name, ITEM_MAPPING, TRAIT_MAPPING

def filter_matches(user_matches, filters):
    filtered_matches = []

    for match in user_matches:
        match_valid = True

        for unit in match['units']:
            champion = get_champion_name(unit)
            if 'champion' in filters and champion != filters['champion']:
                continue

            if 'items' in filters:
                unit_items = []
                for item_name in unit.get('itemNames', []):
                    if len(item_name.split('_')) >= 3:
                        clean_item = item_name.split('_')[-1]
                        mapped_item = ITEM_MAPPING.get(clean_item, clean_item)
                        unit_items.append(mapped_item)

                required_items = filters['items']
                if not all(item in unit_items for item in required_items):
                    continue

            if 'star_level' in filters:
                unit_stars = unit.get('tier',1)
                if unit_stars != filters['star_level']:
                    continue
            
            match_copy = match.copy()
            match_copy['matched_unit'] = {
                'champion': champion,
                'items': unit_items if 'items' in filters else [],
                'stars': unit.get('tier', 1),
                'character_id': unit['character_id']
            }

            filtered_matches.append(match_copy)
            break
    return filtered_matches
    
def explorer_query(puuid, **filters):
    user_matches = get_player_matches(puuid)
    if not user_matches:
        print('No matches found')
        return
    
    filtered_matches = filter_matches(user_matches, filters)

    if not filtered_matches:
        print('No matches found with these filters')
        return

    placements = [match['placement'] for match in filtered_matches]
    avg_placement = sum(placements) / len(placements)
    top4_count = sum(1 for p in placements if p <= 4)
    top4_rate = (top4_count / len(placements)) * 100
    win_count = sum(1 for p in placements if p == 1)
    win_rate = (win_count / len(placements)) * 100

    print(f'\n Explorer Results:')
    print(f' Matches found: {len(filtered_matches)}')
    print(f'Average placement: {avg_placement:.2f}')
    print(f'Top 4 rate: {top4_rate:.2f}% ({top4_count}/{len(placements)})')
    print(f'Win rate: {win_rate:.2f}% ({win_count}/{len(placements)})')
    print(f'Placements: {sorted(placements)}')

    print(f'\n Match details:')
    for i, match in enumerate(filtered_matches,1):
        unit = match['matched_unit']
        items_str = ' + '.join(unit['items']) if unit['items'] else 'No items'
        print(f' {i}. {unit['champion']} {unit['stars']}★ ({items_str}) -> Placement {match['placement']})')

    return {
        'matches': filtered_matches,
        'stats': {
            'avg_placement': avg_placement,
            'top4_rate': top4_rate,
            'win_rate': win_rate,
            'total_matches': len(filtered_matches)
        }
    }

def analyze_explorer_data(puuid):  
    user_matches = get_player_matches(puuid)

    if not user_matches:
        print('No matches found')
        return
    
    print('Explorer data')

    champion_builds = {}
    all_items = set()
    all_traits = set()

    for match in user_matches:
        placement = match['placement']

        for unit in match['units']:
            champion = get_champion_name(unit)

            items = []

            for item_name in unit.get('itemNames', []):
                if len(item_name.split('_')) >=3:
                    clean_item = item_name.split('_')[2]
                    mapped_item = ITEM_MAPPING.get(clean_item, clean_item)
                    items.append(mapped_item)
                    all_items.add(mapped_item)

            item_keys = tuple(sorted(items))
            if champion not in champion_builds:
                champion_builds[champion] = {}

            if item_keys not in champion_builds[champion]:
                champion_builds[champion][item_keys] = {'placement': [], 'count': 0}

            champion_builds[champion][item_keys]['placement'].append(placement)
            champion_builds[champion][item_keys]['count'] += 1
        
        for trait in match['traits']:
            if trait['tier_current'] >0:
                clean_trait = trait['name'].split('_')[1]
                mapped_trait = TRAIT_MAPPING.get(clean_trait, clean_trait)
                trait_info = f'{trait['num_units']} {mapped_trait}'
                all_traits.add(trait_info)

    print(f'\nChampion builds')
    for champion, builds in champion_builds.items():
        if any(build['count'] >=2 for build in builds.values()):
            print(f'\n{champion}:')
            for items,data in sorted(builds.items(), key = lambda x: x[1]['count'], reverse = True):
                if data['count'] >=2:
                    avg_placement = sum(data['placement']) / len(data['placement'])
                    items_str = ' + '.join(items) if items else 'No items'
                    print(f'  {items_str}: {data['count']} games, {avg_placement:.2f} avg placement')
            
    print(f'\n Available items ({len(all_items)}):')
    items_list = sorted(list(all_items))
    for i in range(0, len(items_list),5):
        print(' ' + ', '.join(items_list[i:i+5]))

    print(f'\n Traits played ({len(all_traits)}):')
    traits_list = sorted(list(all_traits))
    for i in range(0, len(traits_list),3):
        print(' ' + ', '.join(traits_list[i:i+3]))

    return {
        'matches': user_matches,
        'champion_builds': champion_builds,
        'available_items': all_items,
        'available_traits': all_traits
    }

if __name__ == '__main__':
    from tft import update_player_data
    puuid = update_player_data('Tourtipouss', '9861', max_matches=5)
    data = analyze_explorer_data(puuid)

    print('\n' + "="*50)
    print('Test explorer')

    print('\n2. Jhin with deathblade')
    explorer_query(puuid, champion='Jhin', items=['Deathblade'])
