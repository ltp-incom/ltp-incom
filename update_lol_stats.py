import os
import re
import requests
from urllib.parse import quote
import base64

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

def get_tier_config(tier):
    """Get color and gradient configuration for tier"""
    configs = {
        'IRON': {
            'color': '#593E35',
            'gradient': 'linear-gradient(135deg, #593E35 0%, #3E2723 100%)',
            'shadow': '0 0 30px rgba(89, 62, 53, 0.5)',
            'emoji': '⚙️'
        },
        'BRONZE': {
            'color': '#CD7F32',
            'gradient': 'linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)',
            'shadow': '0 0 30px rgba(205, 127, 50, 0.5)',
            'emoji': '🥉'
        },
        'SILVER': {
            'color': '#C0C0C0',
            'gradient': 'linear-gradient(135deg, #E0E0E0 0%, #9E9E9E 100%)',
            'shadow': '0 0 30px rgba(192, 192, 192, 0.5)',
            'emoji': '🥈'
        },
        'GOLD': {
            'color': '#FFD700',
            'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA000 100%)',
            'shadow': '0 0 30px rgba(255, 215, 0, 0.5)',
            'emoji': '🥇'
        },
        'PLATINUM': {
            'color': '#00CED1',
            'gradient': 'linear-gradient(135deg, #00CED1 0%, #00838F 100%)',
            'shadow': '0 0 30px rgba(0, 206, 209, 0.5)',
            'emoji': '💎'
        },
        'EMERALD': {
            'color': '#50C878',
            'gradient': 'linear-gradient(135deg, #50C878 0%, #2E7D32 100%)',
            'shadow': '0 0 30px rgba(80, 200, 120, 0.5)',
            'emoji': '💚'
        },
        'DIAMOND': {
            'color': '#B9F2FF',
            'gradient': 'linear-gradient(135deg, #B9F2FF 0%, #64B5F6 100%)',
            'shadow': '0 0 30px rgba(185, 242, 255, 0.5)',
            'emoji': '💠'
        },
        'MASTER': {
            'color': '#BA55D3',
            'gradient': 'linear-gradient(135deg, #BA55D3 0%, #7B1FA2 100%)',
            'shadow': '0 0 30px rgba(186, 85, 211, 0.5)',
            'emoji': '🔮'
        },
        'GRANDMASTER': {
            'color': '#FF4500',
            'gradient': 'linear-gradient(135deg, #FF4500 0%, #D32F2F 100%)',
            'shadow': '0 0 30px rgba(255, 69, 0, 0.5)',
            'emoji': '🔥'
        },
        'CHALLENGER': {
            'color': '#F0E68C',
            'gradient': 'linear-gradient(135deg, #F0E68C 0%, #F9A825 100%)',
            'shadow': '0 0 30px rgba(240, 230, 140, 0.5)',
            'emoji': '👑'
        }
    }
    return configs.get(tier, {
        'color': '#666666',
        'gradient': 'linear-gradient(135deg, #666666 0%, #333333 100%)',
        'shadow': '0 0 30px rgba(102, 102, 102, 0.5)',
        'emoji': '❓'
    })

def create_svg_badge(stats):
    """Create custom SVG badge with modern design"""
    if stats:
        wins = stats['wins']
        losses = stats['losses']
        total = wins + losses
        winrate = round((wins / total * 100), 1) if total > 0 else 0
        tier = stats['tier']
        rank = stats['rank']
        lp = stats['leaguePoints']
        tier_config = get_tier_config(tier)
        
        # Calculate win rate arc
        win_angle = (winrate / 100) * 360
        
        # Add trolling elements for low winrate
        loss_emoji = "😭" if winrate < 40 else "😢" if winrate < 45 else "😔" if winrate < 50 else "😐"
        winrate_color = "#FF0000" if winrate < 40 else "#FF6600" if winrate < 45 else "#FFA500" if winrate < 50 else tier_config['color']
        
        svg_content = f"""<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0F0F0F;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1A1A1A;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="tierGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{tier_config['color']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{tier_config['color']};stop-opacity:0.6" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#2A2A2A" stroke-width="1" opacity="0.2"/>
    </pattern>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="400" fill="url(#bgGradient)" rx="20"/>
  <rect width="800" height="400" fill="url(#grid)" rx="20"/>
  
  <!-- Glow effect (red for low WR) -->
  <ellipse cx="400" cy="200" rx="300" ry="150" fill="{winrate_color}" opacity="0.1" filter="url(#glow)"/>
  
  <!-- Title -->
  <text x="400" y="50" font-family="Arial, sans-serif" font-size="28" font-weight="bold" text-anchor="middle" fill="#FFFFFF">
    {GAME_NAME}#{TAG_LINE} {loss_emoji}
  </text>
  
  <!-- Tier Badge with Warning -->
  <g transform="translate(400, 120)">
    <circle r="60" fill="none" stroke="#333333" stroke-width="8"/>
    <circle r="60" fill="none" stroke="{winrate_color}" stroke-width="8" 
            stroke-dasharray="{win_angle * 0.628} {(360 - win_angle) * 0.628}"
            transform="rotate(-90)" stroke-linecap="round"/>
    <text y="8" font-family="Arial, sans-serif" font-size="32" font-weight="bold" 
          text-anchor="middle" fill="{tier_config['color']}">{tier_config['emoji']}</text>
    {f'<text y="-80" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#FF0000">⚠️ LOW WR WARNING ⚠️</text>' if winrate < 45 else ''}
  </g>
  
  <!-- Rank Info -->
  <text x="400" y="230" font-family="Arial, sans-serif" font-size="36" font-weight="bold" 
        text-anchor="middle" fill="{tier_config['color']}" filter="url(#glow)">
    {tier} {rank}
  </text>
  <text x="400" y="260" font-family="Arial, sans-serif" font-size="20" text-anchor="middle" fill="#CCCCCC">
    {lp} LP {f'(Dropping fast! 📉)' if winrate < 45 else ''}
  </text>
  
  <!-- Stats with color coding -->
  <g transform="translate(200, 320)">
    <rect x="-80" y="-30" width="160" height="60" rx="10" fill="#1E1E1E" stroke="{winrate_color}" stroke-width="2"/>
    <text y="-5" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#AAAAAA">WIN RATE</text>
    <text y="18" font-family="Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle" fill="{winrate_color}">{winrate}%</text>
  </g>
  
  <g transform="translate(400, 320)">
    <rect x="-80" y="-30" width="160" height="60" rx="10" fill="#1E1E1E" stroke="#4CAF50" stroke-width="2"/>
    <text y="-5" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#AAAAAA">WINS</text>
    <text y="18" font-family="Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle" fill="#4CAF50">{wins}</text>
  </g>
  
  <g transform="translate(600, 320)">
    <rect x="-80" y="-30" width="160" height="60" rx="10" fill="#1E1E1E" stroke="#F44336" stroke-width="2"/>
    <text y="-5" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#AAAAAA">LOSSES</text>
    <text y="18" font-family="Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle" fill="#F44336">{losses} 🔥</text>
  </g>
</svg>"""
    else:
        svg_content = f"""<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0F0F0F;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1A1A1A;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#2A2A2A" stroke-width="1" opacity="0.2"/>
    </pattern>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="400" fill="url(#bgGradient)" rx="20"/>
  <rect width="800" height="400" fill="url(#grid)" rx="20"/>
  
  <!-- Title -->
  <text x="400" y="80" font-family="Arial, sans-serif" font-size="28" font-weight="bold" text-anchor="middle" fill="#FFFFFF">
    {GAME_NAME}#{TAG_LINE}
  </text>
  
  <!-- Unranked Icon -->
  <circle cx="400" cy="180" r="60" fill="none" stroke="#666666" stroke-width="8" stroke-dasharray="10 5"/>
  <text x="400" y="195" font-family="Arial, sans-serif" font-size="48" text-anchor="middle" fill="#666666">?</text>
  
  <!-- Status -->
  <text x="400" y="280" font-family="Arial, sans-serif" font-size="36" font-weight="bold" 
        text-anchor="middle" fill="#FF4444" filter="url(#glow)">
    UNRANKED
  </text>
  <text x="400" y="320" font-family="Arial, sans-serif" font-size="18" text-anchor="middle" fill="#AAAAAA">
    Too scared for ranked? Time to prove yourself!
  </text>
</svg>"""
    
    # Encode SVG to base64 for embedding
    svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

def get_roast_message(winrate, losses, wins):
    """Get a roast message based on performance"""
    loss_diff = losses - wins
    if winrate < 30:
        return "🚨 EMERGENCY: Call 911, this winrate needs medical attention! 🚨"
    elif winrate < 40:
        return "💀 RIP MMR (2024-2025) - Gone but not forgotten 💀"
    elif winrate < 45:
        return "🎪 Welcome to the circus! You must be the main clown 🤡"
    elif winrate < 48:
        return "📉 Stonks? More like STINKS! 📉"
    elif winrate < 50:
        return "🎰 So close to 50%... yet so far 🎰"
    elif loss_diff > 50:
        return f"🏔️ That's a {loss_diff} loss mountain to climb! Good luck! 🏔️"
    elif loss_diff > 20:
        return f"🕳️ Currently in a {loss_diff} game hole. Keep digging! 🕳️"
    else:
        return "🎯 Actually decent... wait, wrong account? 🎯"

def get_achievement_badges(stats):
    """Generate sarcastic achievement badges"""
    wins = stats['wins']
    losses = stats['losses']
    total = wins + losses
    winrate = round((wins / total * 100), 1) if total > 0 else 0
    loss_diff = losses - wins
    
    achievements = []
    
    if winrate < 40:
        achievements.append("🏆 **40% Club Member** - Elite underperformer")
    if losses > 200:
        achievements.append("💯 **Loss Centurion** - 200+ defeats and counting!")
    if loss_diff > 69:
        achievements.append("🌊 **Tsunami of Ls** - Drowning in defeats")
    if winrate < 45 and total > 100:
        achievements.append("🎮 **Consistency King** - Consistently bad!")
    if losses > wins * 1.5:
        achievements.append("📊 **Statistical Anomaly** - How is this even possible?")
    
    return achievements

def update_readme(stats):
    """Update README with enhanced visual stats"""
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    svg_url = create_svg_badge(stats)
    
    if stats:
        wins = stats['wins']
        losses = stats['losses']
        total = wins + losses
        winrate = round((wins / total * 100), 1) if total > 0 else 0
        tier = stats['tier']
        tier_config = get_tier_config(tier)
        loss_diff = losses - wins
        
        # Performance indicator
        performance = "🔥 ON FIRE!" if winrate >= 60 else "📈 Climbing" if winrate >= 52 else "⚖️ Balanced" if winrate >= 48 else "📉 Struggling"
        
        # Get roast and achievements
        roast = get_roast_message(winrate, losses, wins)
        achievements = get_achievement_badges(stats)
        
        # Calculate estimated time wasted (assuming 30 min per loss)
        time_wasted = (losses * 30) // 60
        days_wasted = time_wasted // 24
        
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">
  
# {tier_config['emoji']} League of Legends Stats {tier_config['emoji']}

<img src="{svg_url}" alt="LoL Stats" width="800"/>

### 💬 {roast}

---

### 📊 Performance Analysis

<table>
  <tr>
    <td align="center">
      <h3>🎯 Current Status</h3>
      <b>{performance}</b>
    </td>
    <td align="center">
      <h3>🏆 Games Played</h3>
      <b>{total}</b>
    </td>
    <td align="center">
      <h3>📈 Win Difference</h3>
      <b style="color: {'green' if wins > losses else 'red'}">{'+' if wins > losses else ''}{wins - losses}</b>
    </td>
  </tr>
</table>

{f'''### 🏅 Special Achievements
{chr(10).join(achievements)}
''' if achievements else ''}

### 📈 Fun Facts
- **⏰ Time spent losing:** ~{time_wasted} hours ({days_wasted} days)
- **💔 Dreams crushed:** {losses}
- **🎲 Coinflip performance:** {'WORSE than a coin' if winrate < 50 else 'Slightly better than a coin'}
- **📉 Chance of reaching 50% WR:** {f"Need {loss_diff} straight wins!" if loss_diff > 0 else "Already there!"}

<details>
<summary><b>🔍 Detailed Stats (click if you dare)</b></summary>

- **Matches where team said "gg wp":** Probably {wins}
- **Matches where team said "report [champion]":** Definitely {losses}
- **Times blamed jungler:** {losses}
- **Times it was actually your fault:** Also {losses}
- **Current mental state:** {'☠️ Dead inside' if winrate < 45 else '😔 Questioning life choices' if winrate < 50 else '😤 Copium overdose'}

</details>

<br/>

> **[{GITHUB_USERNAME}](https://github.com/{GITHUB_USERNAME})** | Region: **{PLATFORM.upper()}** | Updated: **{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}**
> 
> *"It's not about winning, it's about having fun"* - {GAME_NAME}, probably

</div>
<!-- LOL-STATS:END -->"""
    else:
        badges_section = f"""<!-- LOL-STATS:START -->
<div align="center">

# 🎮 League of Legends Stats 🎮

<img src="{svg_url}" alt="LoL Stats" width="800"/>

---

### 💪 Ready to Start Your Ranked Journey?

<table>
  <tr>
    <td align="center">
      <h3>🎯 Status</h3>
      <b>Placement Matches Awaiting</b>
    </td>
    <td align="center">
      <h3>🎮 Next Step</h3>
      <b>Queue Up for Ranked!</b>
    </td>
  </tr>
</table>

<br/>

> **[{GITHUB_USERNAME}](https://github.com/{GITHUB_USERNAME})** | Region: **{PLATFORM.upper()}** | Updated: **{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}**

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
        update_readme(None)
        print(f"❌ {GAME_NAME}#{TAG_LINE} - Account not found")
        print(f"💭 Maybe they uninstalled after seeing their stats? 🤔")
        return
    
    stats = get_ranked_stats(account['puuid'], PLATFORM)
    
    update_readme(stats)
    
    if stats:
        wins = stats['wins']
        losses = stats['losses']
        total = wins + losses
        winrate = round((wins / total * 100), 1) if total > 0 else 0
        loss_diff = losses - wins
        
        print(f"✅ Updated README for {GAME_NAME}#{TAG_LINE}")
        print(f"📊 {stats['tier']} {stats['rank']} - {winrate}% WR ({wins}W/{losses}L)")
        
        # Roast based on performance
        if winrate < 40:
            print(f"🚨 YIKES! {winrate}% win rate detected! Calling emergency services... 🚑")
        elif winrate < 45:
            print(f"😬 {winrate}%... That's rough buddy. Have you tried Minecraft? 🎮")
        elif winrate < 48:
            print(f"🎯 So close to 50%... yet so far! Keep grinding (or uninstall) 💪")
        elif loss_diff > 50:
            print(f"🏔️ You're {loss_diff} losses deep! That's a whole Everest to climb! 🧗")
        elif loss_diff > 20:
            print(f"📉 {loss_diff} more losses than wins... F in the chat boys 😔")
        
        if losses > 200:
            print(f"🏆 Achievement Unlocked: 200+ losses! Your commitment to losing is admirable! 👏")
            
        if total > 500 and winrate < 48:
            print(f"🤯 {total} games with {winrate}% WR... Definition of insanity right there!")
    else:
        print(f"✅ Updated README for {GAME_NAME}#{TAG_LINE}")
        print(f"❌ UNRANKED - No ranked games found")
        print(f"🐔 Too scared for ranked? Or saving their mental? Smart move! 🧠")

if __name__ == "__main__":
    main()
