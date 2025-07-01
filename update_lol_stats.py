import os
import re
import requests
from urllib.parse import quote

GAME_NAME = "wokobo"
TAG_LINE = "6969"
PLATFORM = "euw1"
REGION = "EUROPE"

RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

def get_account_by_riot_id(game_name, tag_line, region):
    """Get account data using Riot ID"""
    encoded_game_name = quote(game_name)
    encoded_tag_line = quote(tag_line)
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"Account not found: {game_name}#{tag_line}")
        return None
    else:
        print(f"Error getting account: {response.status_code} - {response.text}")
        return None

def get_summoner_by_puuid(puuid, platform):
    """Get summoner data from PUUID"""
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting summoner: {response.status_code}")
        return None

def get_ranked_stats(summoner_id, platform):
    """Get ranked stats for summoner"""
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    response = requests.get(url, headers=headers)
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
        
        tier_color = get_tier_color(tier)
        wr_color = get_winrate_color(winrate)
        
        if tier in ['IRON', 'BRONZE']:
            roast = "🗑️ ELO HELL RESIDENT 🗑️"
            subtitle = f"### {roast} {display_name}'s Abysmal Stats {roast}"
            extra_badge = f"![Status](https://img.shields.io/badge/Skill-404%20NOT%20FOUND-ff0000?style=for-the-badge)"
        elif winrate < 45:
            roast = "🔥 HARDSTUCK ALERT 🔥"
            subtitle = f"### {roast} {display_name}'s Tragic League Stats {roast}"
            extra_badge = f"![Status](https://img.shields.io/badge/Status-WASHED-ff0000?style=for-the-badge)"
        elif winrate < 48:
            roast = "⚠️"
            subtitle = f"### {roast} {display_name}'s Questionable Performance {roast}"
            extra_badge = f"![Status](https://img.shields.io/badge/Mental-BOOM-orange?style=for-the-badge)"
        elif winrate < 50:
            roast = "😬"
            subtitle = f"### {roast} {display_name} Almost at 50% Copium {roast}"
            extra_badge = f"![Status](https://img.shields.io/badge/Copium-MAXIMUM-yellow?style=for-the-badge)"
        else:
            roast = ""
            subtitle = f"### 🎮 {display_name}'s League Stats"
            extra_badge = ""
        
        # Calculate loss streak messaging
        loss_diff = losses - wins
        streak_msg = f"**Currently {loss_diff} more losses than wins!** 📉" if loss_diff > 0 else ""
        
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">
  
# 🚨 PUBLIC SERVICE ANNOUNCEMENT 🚨

{subtitle}

![Rank](https://img.shields.io/badge/Rank-{tier}%20{rank}-{tier_color}?style=for-the-badge&logo=riot-games&logoColor=white)
![LP](https://img.shields.io/badge/LP-{lp}-blue?style=for-the-badge)
![Winrate](https://img.shields.io/badge/Winrate-{winrate}%25-{wr_color}?style=for-the-badge)
![Games](https://img.shields.io/badge/Games-{total}-lightgrey?style=for-the-badge)
{extra_badge}

### 📊 Season Performance
**{wins} Wins** vs **{losses} Losses** ({winrate}% WR)

{streak_msg}

{f"*Maybe it's time to uninstall?* 🎯" if winrate < 45 else ""}
{f"*Skill issue confirmed* 🎮" if tier in ['IRON', 'BRONZE'] else ""}
{f"*The grind continues... downward* 📉" if 45 <= winrate < 50 else ""}

---
</div>
<!-- LOL-STATS:END -->"""
    else:
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

# 🚨 BREAKING NEWS 🚨
### {display_name} is TOO SCARED to play ranked

![Status](https://img.shields.io/badge/Status-UNRANKED-grey?style=for-the-badge)
![Courage](https://img.shields.io/badge/Courage-NOT%20FOUND-red?style=for-the-badge)
![Excuse](https://img.shields.io/badge/Excuse-"Just%20Warming%20Up"-yellow?style=for-the-badge)

*Hiding in ARAM and normals* 🏃‍♂️💨

---
</div>
<!-- LOL-STATS:END -->"""
    
    pattern = r'<!-- LOL-STATS:START -->.*?<!-- LOL-STATS:END -->'
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, badges_section, content, flags=re.DOTALL)
    else:
        new_content = content + '\n\n' + badges_section
    
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(new_content)

def main():
    try:
        print(f"Looking up {GAME_NAME}#{TAG_LINE}...")
        
        account = get_account_by_riot_id(GAME_NAME, TAG_LINE, REGION)
        if not account:
            print(f"Account {GAME_NAME}#{TAG_LINE} not found")
            update_readme_with_badges(None, GAME_NAME, TAG_LINE)
            return
        
        puuid = account['puuid']
        print(f"Found account with PUUID: {puuid}")
        
        summoner = get_summoner_by_puuid(puuid, PLATFORM)
        if not summoner:
            print("Could not get summoner data")
            update_readme_with_badges(None, GAME_NAME, TAG_LINE)
            return
        
        stats = get_ranked_stats(summoner['id'], PLATFORM)
        
        update_readme_with_badges(stats, GAME_NAME, TAG_LINE)
        
        if stats:
            winrate = round((stats['wins'] / (stats['wins'] + stats['losses']) * 100), 1)
            print(f"Updated badges for {GAME_NAME}#{TAG_LINE}: {stats['tier']} {stats['rank']} - {winrate}% WR")
        else:
            print(f"Updated badges for {GAME_NAME}#{TAG_LINE} (Unranked)")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()