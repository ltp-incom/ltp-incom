import os
import re
import requests
import json
from urllib.parse import quote

GAME_NAME = "wokobo"
TAG_LINE = "6969"
PLATFORM = "euw1"
REGION = "europe"
GITHUB_USERNAME = "cme-incom"

RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

def get_account_by_riot_id(game_name, tag_line, region):
    """Get account data using Riot ID"""
    encoded_game_name = quote(game_name)
    encoded_tag_line = quote(tag_line)
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    print(f"\n🔍 DEBUG: Fetching account from URL: {url}")
    
    response = requests.get(url, headers=headers)
    print(f"📡 DEBUG: Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ DEBUG: Account data received: {json.dumps(data, indent=2)}")
        return data
    elif response.status_code == 404:
        print(f"❌ Account not found: {game_name}#{tag_line}")
        return None
    else:
        print(f"❌ Error getting account: {response.status_code} - {response.text}")
        return None

def get_summoner_by_puuid(puuid, platform):
    """Get summoner data from PUUID"""
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    print(f"\n🔍 DEBUG: Fetching summoner from URL: {url}")
    
    response = requests.get(url, headers=headers)
    print(f"📡 DEBUG: Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ DEBUG: Summoner data received: {json.dumps(data, indent=2)}")
        return data
    else:
        print(f"❌ Error getting summoner: {response.status_code} - {response.text}")
        return None

def get_ranked_stats(puuid, platform):
    """Get ranked stats for summoner using PUUID"""
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    print(f"\n🔍 DEBUG: Fetching ranked stats from URL: {url}")
    print(f"🔑 DEBUG: Using API Key: {RIOT_API_KEY[:20]}...")
    
    response = requests.get(url, headers=headers)
    print(f"📡 DEBUG: Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ DEBUG: Ranked data received: {json.dumps(data, indent=2)}")
        
        if not data:
            print("⚠️ DEBUG: Player has no ranked data (empty response)")
            return None
        
        for queue in data:
            if queue['queueType'] == 'RANKED_SOLO_5x5':
                print(f"🎮 DEBUG: Found Solo/Duo queue data: {json.dumps(queue, indent=2)}")
                return queue
        print("⚠️ DEBUG: No Solo/Duo ranked data found (might only have Flex)")
        
        queue_types = [q['queueType'] for q in data]
        print(f"📋 DEBUG: Available queues: {queue_types}")
        
    elif response.status_code == 403:
        print("❌ DEBUG: 403 Forbidden - Check if your API key is valid and not expired")
        print(f"❌ DEBUG: Response: {response.text}")
    elif response.status_code == 429:
        print("❌ DEBUG: 429 Rate Limited - Too many requests")
    else:
        print(f"❌ DEBUG: Error {response.status_code} - {response.text}")
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

def get_winrate_color(winrate):
    """Get color for winrate"""
    if winrate >= 60:
        return 'brightgreen'
    elif winrate >= 52:
        return 'green'
    elif winrate >= 48:
        return 'yellow'
    else:
        return 'red'

def update_readme_with_badges(stats, game_name, tag_line):
    """Update README with badge URLs"""
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
        
        print(f"\n📊 DEBUG: Final stats - Tier: {tier} {rank}, LP: {lp}, Wins: {wins}, Losses: {losses}, WR: {winrate}%")
        
        tier_color = get_tier_color(tier)
        wr_color = get_winrate_color(winrate)
        
        if winrate < 45:
            status_msg = "⚠️ CRITICAL ⚠️"
        elif winrate < 50:
            status_msg = "📉 STRUGGLING 📉"
        else:
            status_msg = "📊 STATS 📊"
        
        loss_diff = losses - wins
        
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

## {display_name.upper()} (@{GITHUB_USERNAME}) WINRATE IS

# {winrate}%

![Rank](https://img.shields.io/badge/{tier}%20{rank}-{lp}%20LP-{tier_color}?style=for-the-badge)
![Record](https://img.shields.io/badge/{wins}W%20{losses}L-{total}%20Games-333333?style=for-the-badge)
{f'![Diff](https://img.shields.io/badge/↓{loss_diff}%20MORE%20LOSSES-ff0000?style=for-the-badge)' if loss_diff > 0 else ''}

{status_msg}

</div>
<!-- LOL-STATS:END -->"""
    else:
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

## {display_name.upper()} (@{GITHUB_USERNAME}) IS

# UNRANKED

![Status](https://img.shields.io/badge/TOO%20SCARED%20FOR%20RANKED-ff0000?style=for-the-badge)
![Games](https://img.shields.io/badge/0%20RANKED%20GAMES-333333?style=for-the-badge)

🐔 CURRENTLY HIDING IN NORMALS 🐔

</div>
<!-- LOL-STATS:END -->"""
    
    pattern = r'<!-- LOL-STATS:START -->.*?<!-- LOL-STATS:END -->'
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, badges_section, content, flags=re.DOTALL)
    else:
        new_content = badges_section + '\n\n' + content
    
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("\n✅ README updated successfully!")

def get_winrate_emoji(winrate):
    """Get emoji based on winrate"""
    if winrate >= 60:
        return "🔥🔥🔥"
    elif winrate >= 55:
        return "🔥🔥"
    elif winrate >= 52:
        return "🔥"
    elif winrate >= 50:
        return "😐"
    elif winrate >= 48:
        return "😰"
    elif winrate >= 45:
        return "😱"
    else:
        return "💀💀💀"

def test_api_key():
    """Test if the API key is valid"""
    test_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/test/test"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    print(f"\n🔑 Testing API key...")
    response = requests.get(test_url, headers=headers)
    
    if response.status_code == 404:
        print("✅ API key is valid (got expected 404 for fake account)")
        return True
    elif response.status_code == 403:
        print("❌ API key is invalid or has expired!")
        return False
    elif response.status_code == 401:
        print("❌ API key is missing or malformed!")
        return False
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        return True

def main():
    try:
        print("=" * 50)
        print(f"🎮 LoL Stats Updater - Debug Mode 🎮")
        print(f"Looking up: {GAME_NAME}#{TAG_LINE}")
        print(f"Region: {REGION} | Platform: {PLATFORM}")
        print("=" * 50)
        
        if not RIOT_API_KEY:
            print("❌ ERROR: RIOT_API_KEY not found in environment variables!")
            print("Available env vars:", list(os.environ.keys()))
            return
        else:
            print(f"✅ API Key found")
            print(f"✅ API Key length: {len(RIOT_API_KEY)} characters")
        
        if not test_api_key():
            print("\n❌ Aborting due to invalid API key")
            return
        
        account = get_account_by_riot_id(GAME_NAME, TAG_LINE, REGION)
        if not account:
            print(f"\n❌ Account {GAME_NAME}#{TAG_LINE} not found")
            update_readme_with_badges(None, GAME_NAME, TAG_LINE)
            return
        
        puuid = account['puuid']
        print(f"\n✅ Found account with PUUID: {puuid}")
        
        summoner = get_summoner_by_puuid(puuid, PLATFORM)
        if summoner:
            print(f"\n✅ Found summoner ID: {summoner['id']}")
            print(f"   Summoner Level: {summoner.get('summonerLevel', 'Unknown')}")
        else:
            print("\n⚠️ Could not get summoner data (but continuing with PUUID)")
        
        stats = get_ranked_stats(puuid, PLATFORM)
        
        update_readme_with_badges(stats, GAME_NAME, TAG_LINE)
        
        if stats:
            winrate = round((stats['wins'] / (stats['wins'] + stats['losses']) * 100), 1)
            print(f"\n🏆 Final Result: {GAME_NAME}#{TAG_LINE}")
            print(f"   Rank: {stats['tier']} {stats['rank']}")
            print(f"   LP: {stats['leaguePoints']}")
            print(f"   Record: {stats['wins']}W - {stats['losses']}L")
            print(f"   Winrate: {winrate}%")
        else:
            print(f"\n⚠️ {GAME_NAME}#{TAG_LINE} is UNRANKED")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()