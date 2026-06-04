import urllib.request
import json
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

players = {
    'spain': 'Lamine Yamal',
    'argentina': 'Lionel Messi',
    'france': 'Kylian Mbappe',
    'england': 'Jude Bellingham',
    'brazil': 'Vinicius Junior',
    'portugal': 'Cristiano Ronaldo',
    'netherlands': 'Virgil van Dijk',
    'germany': 'Thomas Muller',
    'colombia': 'Luis Diaz',
    'croatia': 'Luka Modric'
}

for team, player in players.items():
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={urllib.parse.quote(player)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data['player'] and len(data['player']) > 0:
                cutout_url = data['player'][0].get('strCutout')
                if cutout_url:
                    urllib.request.urlretrieve(cutout_url, f"/Users/mukilan/FIFA 2026 WINNER PREDICTION MODEL/web_app/public/{team}_cutout.png")
                    print(f"Downloaded cutout for {player}")
                else:
                    print(f"No cutout found for {player}")
            else:
                print(f"Player {player} not found")
    except Exception as e:
        print(f"Error downloading {player}: {e}")
