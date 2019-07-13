import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) \
                   Chrome/47.0.2526.106 Safari/537.36'
}

page = 'https://www.transfermarkt.com.br/se-palmeiras-\
        sao-paulo/kader/verein/1023/saison_id/2018'

pageTree = requests.get(page, headers=headers)
pageSoup = BeautifulSoup(pageTree.content, 'html.parser')

raw_players = pageSoup.find_all('tr', {'class': ['odd', 'even']})

players = []

for raw_player in raw_players:
    players.append({
        'name': raw_player.find_all('a', {'class': 'spielprofil_tooltip'})[0].text,
        'position': raw_player.find_all('td')[4].text,
        'number' : raw_player.find_all('div', {'class': 'rn_nummer'})[0].text,
        'market_value': raw_player.find_all('td', {'class': 'rechts hauptlink'})[0].text.split('€')[0] + '€', 
        'age': raw_player.find_all('td', {'class': 'zentriert'})[1].text.split(' ')[1].replace('(', '').replace(')', ''),
        'date_of_birth': raw_player.find_all('td', {'class': 'zentriert'})[1].text.split(' ')[0],
        'nation': raw_player.find_all('img', {'class': 'flaggenrahmen'})[0]['title'],
        'contract_expires': raw_player.find_all('td', {'class': 'zentriert'})[3].text.replace('.', '/')
    })

for player in players:
    print('\n', player, '\n')

def make_request(url):
    pass

def extract_clubs_urls(raw_data):
    pass

def extract_players_info(raw_data):
    pass

def extract_manager_info(raw_data):
    pass

def extract_club_info(raw_data):
    pass

def extract_league_info(raw_data):
    pass