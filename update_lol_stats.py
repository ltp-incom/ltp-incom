import os
import re
import requests
import json
from urllib.parse import quote

GAME_NAME = "wokobo"
TAG_LINE = "6969"
PLATFORM = "euw1"
REGION = "europe"

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

def get_ranked_stats(summoner_id, platform):
    """Get ranked stats for summoner"""
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    print(f"\n🔍 DEBUG: Fetching ranked stats from URL: {url}")
    
    response = requests.get(url, headers=headers)
    print(f"📡 DEBUG: Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ DEBUG: Ranked data received: {json.dumps(data, indent=2)}")
        
        for queue in data:
            if queue['queueType'] == 'RANKED_SOLO_5x5':
                print(f"🎮 DEBUG: Found Solo/Duo queue data: {json.dumps(queue, indent=2)}")
                return queue
        print("⚠️ DEBUG: No Solo/Duo ranked data found")
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
        
        if tier in ['IRON', 'BRONZE']:
            roast = "💩 ROCK BOTTOM GAMING 💩"
            subtitle = f"### {roast}<br/>📢 {display_name} - Professional Feeder 📢"
            extra_badges = f"""
![Status](https://img.shields.io/badge/🎯_Skill_Level-UNDETECTABLE-ff0000?style=for-the-badge&labelColor=000000)
![Talent](https://img.shields.io/badge/🧠_Game_IQ-NEGATIVE-ff0000?style=for-the-badge&labelColor=000000)
![Future](https://img.shields.io/badge/🔮_Peak_Rank-STILL_{tier}-{tier_color}?style=for-the-badge&labelColor=000000)"""
        elif winrate < 45:
            roast = "🔥 SYSTEM MALFUNCTION 🔥"
            subtitle = f"### {roast}<br/>⚠️ {display_name}'s Performance Review: FAILED ⚠️"
            extra_badges = f"""
![Status](https://img.shields.io/badge/💀_Status-WASHED_UP-ff0000?style=for-the-badge&labelColor=000000)
![Diagnosis](https://img.shields.io/badge/🏥_Diagnosis-CHRONIC_FEEDER-ff6600?style=for-the-badge&labelColor=000000)
![Advice](https://img.shields.io/badge/💡_Pro_Tip-UNINSTALL-ff0066?style=for-the-badge&labelColor=000000)"""
        elif winrate < 48:
            roast = "🚨 WARNING 🚨"
            subtitle = f"### {roast}<br/>😰 {display_name} Struggling to Stay Relevant 😰"
            extra_badges = f"""
![Mental](https://img.shields.io/badge/🧠_Mental-BOOM-orange?style=for-the-badge&labelColor=000000)
![Tilt](https://img.shields.io/badge/📐_Tilt_Level-MAXIMUM-ff9900?style=for-the-badge&labelColor=000000)"""
        elif winrate < 50:
            roast = "😬 BARELY HANGING ON 😬"
            subtitle = f"### {roast}<br/>🎪 Welcome to {display_name}'s Clown Fiesta 🎪"
            extra_badges = f"""
![Copium](https://img.shields.io/badge/💊_Copium_Dose-LETHAL-yellow?style=for-the-badge&labelColor=000000)
![Reality](https://img.shields.io/badge/🌍_Reality_Check-PENDING-ffcc00?style=for-the-badge&labelColor=000000)"""
        else:
            roast = ""
            subtitle = f"### 🎮 {display_name}'s League Stats"
            extra_badges = ""
        
        loss_diff = losses - wins
        if loss_diff > 20:
            streak_msg = f"### 📉 DISASTER ALERT: {loss_diff} MORE LOSSES THAN WINS! 📉"
        elif loss_diff > 10:
            streak_msg = f"### ⚠️ Currently {loss_diff} more losses than wins! Time to quit? ⚠️"
        elif loss_diff > 0:
            streak_msg = f"**Currently {loss_diff} more losses than wins!** 📉"
        else:
            streak_msg = ""
        
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=20&height=100&section=header&text=⚠️%20VIEWER%20DISCRETION%20ADVISED%20⚠️&fontSize=30&fontColor=ffffff&animation=twinkling"/>

{subtitle}

<br/>

![Rank](https://img.shields.io/badge/🏆_Rank-{tier}%20{rank}-{tier_color}?style=for-the-badge&logo=riot-games&logoColor=white&labelColor=000000)
![LP](https://img.shields.io/badge/🔷_LP-{lp}-0066ff?style=for-the-badge&labelColor=000000)
![Winrate](https://img.shields.io/badge/📊_Winrate-{winrate}%25-{wr_color}?style=for-the-badge&labelColor=000000)
![Games](https://img.shields.io/badge/🎮_Games-{total}-666666?style=for-the-badge&labelColor=000000)
{extra_badges}

<br/>

### 📈 Season {wins + losses} Performance Report 📉

<img src="https://img.shields.io/badge/WINS-{wins}-22c55e?style=flat-square&logo=checkmarx&logoColor=white" height="30"/>
<img src="https://img.shields.io/badge/VS-⚔️-ffffff?style=flat-square" height="30"/>
<img src="https://img.shields.io/badge/LOSSES-{losses}-ef4444?style=flat-square&logo=x&logoColor=white" height="30"/>

### **Winrate: {winrate}%** {get_winrate_emoji(winrate)}

{streak_msg}

{f'<img src="https://img.shields.io/badge/🎯_Recommendation-FIND%20A%20NEW%20GAME-ff0000?style=for-the-badge&labelColor=000000"/>' if winrate < 45 else ""}
{f'<img src="https://img.shields.io/badge/⚠️_Skill%20Issue-CONFIRMED-ff6600?style=for-the-badge&labelColor=000000"/>' if tier in ['IRON', 'BRONZE'] else ""}
{f'<img src="https://img.shields.io/badge/📉_Trajectory-DOWNWARD%20SPIRAL-ff9900?style=for-the-badge&labelColor=000000"/>' if 45 <= winrate < 50 else ""}

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=20&height=60&section=footer&fontSize=20&fontColor=ffffff&animation=twinkling"/>

</div>
<!-- LOL-STATS:END -->"""
    else:
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=100&section=header&text=🚨%20MISSING%20PERSON%20ALERT%20🚨&fontSize=30&fontColor=ffffff&animation=twinkling"/>

### 🔍 LAST SEEN: Hiding in Normal Games 🔍
### 📢 {display_name} - Too Scared for Ranked 📢

<br/>

![Status](https://img.shields.io/badge/🎮_Status-UNRANKED-grey?style=for-the-badge&labelColor=000000)
![Courage](https://img.shields.io/badge/💪_Courage-NOT%20FOUND-ff0000?style=for-the-badge&labelColor=000000)
![Excuse](https://img.shields.io/badge/🎭_Excuse-"Just%20Practicing"-ffcc00?style=for-the-badge&labelColor=000000)
![Reality](https://img.shields.io/badge/🌍_Reality-SCARED%20OF%20RANKED-ff0066?style=for-the-badge&labelColor=000000)

<br/>

### 🏃‍♂️ Currently Hiding In: 🏃‍♂️

<img src="https://img.shields.io/badge/ARAM-✓-22c55e?style=flat-square" height="25"/>
<img src="https://img.shields.io/badge/Normals-✓-22c55e?style=flat-square" height="25"/>
<img src="https://img.shields.io/badge/Bot%20Games-✓-22c55e?style=flat-square" height="25"/>
<img src="https://img.shields.io/badge/Ranked-✗-ef4444?style=flat-square" height="25"/>

<br/>

*"I'm just warming up" - Every unranked player ever* 🤡

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12&height=60&section=footer&fontSize=20&fontColor=ffffff&animation=twinkling"/>

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

def main():
    try:
        print("=" * 50)
        print(f"🎮 LoL Stats Updater - Debug Mode 🎮")
        print(f"Looking up: {GAME_NAME}#{TAG_LINE}")
        print(f"Region: {REGION} | Platform: {PLATFORM}")
        print("=" * 50)
        
        # Check if API key exists
        if not RIOT_API_KEY:
            print("❌ ERROR: RIOT_API_KEY not found in environment variables!")
            return
        else:
            print(f"✅ API Key found")
        
        account = get_account_by_riot_id(GAME_NAME, TAG_LINE, REGION)
        if not account:
            print(f"\n❌ Account {GAME_NAME}#{TAG_LINE} not found")
            update_readme_with_badges(None, GAME_NAME, TAG_LINE)
            return
        
        puuid = account['puuid']
        print(f"\n✅ Found account with PUUID: {puuid}")
        
        summoner = get_summoner_by_puuid(puuid, PLATFORM)
        if not summoner:
            print("\n❌ Could not get summoner data")
            update_readme_with_badges(None, GAME_NAME, TAG_LINE)
            return
        
        print(f"\n✅ Found summoner ID: {summoner['id']}")
        print(f"   Summoner Level: {summoner.get('summonerLevel', 'Unknown')}")
        
        stats = get_ranked_stats(summoner['id'], PLATFORM)
        
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