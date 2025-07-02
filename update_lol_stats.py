import os
import re
import requests
from urllib.parse import quote

GAME_NAME = "wokobo"
TAG_LINE = "6969"
PLATFORM = "euw1"
REGION = "europe"
RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

def get_account_by_riot_id(game_name, tag_line, region):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    return response.json() if response.status_code == 200 else None

def get_ranked_stats(puuid, platform):
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    
    if response.status_code == 200:
        data = response.json()
        for queue in data:
            if queue['queueType'] == 'RANKED_SOLO_5x5':
                return queue
    return None

def update_readme(stats):
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    if stats:
        wins = stats['wins']
        losses = stats['losses']
        total = wins + losses
        winrate = round((wins / total * 100), 1) if total > 0 else 0
        
        content = re.sub(r'<!-- WINS -->.*?<!-- /WINS -->', f'<!-- WINS -->{wins}<!-- /WINS -->', content)
        content = re.sub(r'<!-- LOSSES -->.*?<!-- /LOSSES -->', f'<!-- LOSSES -->{losses}<!-- /LOSSES -->', content)
        content = re.sub(r'<!-- TOTAL -->.*?<!-- /TOTAL -->', f'<!-- TOTAL -->{total}<!-- /TOTAL -->', content)
        content = re.sub(r'<!-- WINRATE -->.*?<!-- /WINRATE -->', f'<!-- WINRATE -->{winrate}<!-- /WINRATE -->', content)
        content = re.sub(r'<!-- TIER -->.*?<!-- /TIER -->', f'<!-- TIER -->{stats["tier"]}<!-- /TIER -->', content)
        content = re.sub(r'<!-- RANK -->.*?<!-- /RANK -->', f'<!-- RANK -->{stats["rank"]}<!-- /RANK -->', content)
        content = re.sub(r'<!-- LP -->.*?<!-- /LP -->', f'<!-- LP -->{stats["leaguePoints"]}<!-- /LP -->', content)
    
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    account = get_account_by_riot_id(GAME_NAME, TAG_LINE, REGION)
    if account:
        stats = get_ranked_stats(account['puuid'], PLATFORM)
        update_readme(stats)

if __name__ == "__main__":
    main()
