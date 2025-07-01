import os
import re
import requests
from urllib.parse import quote

GAME_NAME = "wokobo"
TAG_LINE = "6969"
PLATFORM = "euw1"
REGION = "europe"
GITHUB_USERNAME = "cme-incom"

RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

def get_account_by_riot_id(game_name, tag_line, region):
    """Get account data using Riot ID"""
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    return response.json() if response.status_code == 200 else None

def get_ranked_stats(puuid, platform):
    """Get ranked stats using PUUID"""
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    
    if response.status_code == 200:
        data = response.json()
        for queue in data:
            if queue['queueType'] == 'RANKED_SOLO_5x5':
                return queue
    return None

def get_tier_color(tier):
    """Get color for tier"""
    colors = {
        'IRON': '593E35',
        'BRONZE': 'CD7F32',
        'SILVER': 'C0C0C0',
        'GOLD': 'FFD700',
        'PLATINUM': '00CED1',
        'EMERALD': '50C878',
        'DIAMOND': 'B9F2FF',
        'MASTER': 'BA55D3',
        'GRANDMASTER': 'FF4500',
        'CHALLENGER': 'F0E68C'
    }
    return colors.get(tier, 'blue')

def update_readme(stats, game_name, tag_line):
    """Update README with stats"""
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    display_name = f"{game_name}#{tag_line}"
    
    if stats:
        wins = stats['wins']
        losses = stats['losses']
        total = wins + losses
        winrate = round((wins / total * 100), 1) if total > 0 else 0
        tier = stats['tier']
        rank = stats['rank']
        lp = stats['leaguePoints']
        tier_color = get_tier_color(tier)
        loss_diff = losses - wins
        
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

## {display_name.upper()} (@{GITHUB_USERNAME}) WINRATE IS

# {winrate}%

![Rank](https://img.shields.io/badge/{tier}%20{rank}-{lp}%20LP-{tier_color}?style=for-the-badge)
![Record](https://img.shields.io/badge/{wins}W%20{losses}L-{total}%20Games-333333?style=for-the-badge)
{f'![Diff](https://img.shields.io/badge/↓{loss_diff}%20MORE%20LOSSES-ff0000?style=for-the-badge)' if loss_diff > 0 else ''}

</div>
<!-- LOL-STATS:END -->"""
    else:
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

## {display_name.upper()} (@{GITHUB_USERNAME}) IS

# UNRANKED

![Status](https://img.shields.io/badge/TOO%20SCARED%20FOR%20RANKED-ff0000?style=for-the-badge)

</div>
<!-- LOL-STATS:END -->"""
    
    pattern = r'<!-- LOL-STATS:START -->.*?<!-- LOL-STATS:END -->'
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, badges_section, content, flags=re.DOTALL)
    else:
        new_content = badges_section + '\n\n' + content
    
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(new_content)

def main():
    account = get_account_by_riot_id(GAME_NAME, TAG_LINE, REGION)
    if not account:
        update_readme(None, GAME_NAME, TAG_LINE)
        return
    
    stats = get_ranked_stats(account['puuid'], PLATFORM)
    
    update_readme(stats, GAME_NAME, TAG_LINE)
    
    if stats:
        winrate = round((stats['wins'] / (stats['wins'] + stats['losses']) * 100), 1)
        print(f"{GAME_NAME}#{TAG_LINE}: {stats['tier']} {stats['rank']} - {winrate}% WR")
    else:
        print(f"{GAME_NAME}#{TAG_LINE}: UNRANKED")

if __name__ == "__main__":
    main()