import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = 'https://www.transfermarkt.com.br'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) \
                   Chrome/47.0.2526.106 Safari/537.36'
}

page = 'https://www.transfermarkt.com.br/wettbewerbe/europa'


def make_request(pageUrl):
    pageTree = requests.get(pageUrl, headers=headers)
    pageSoup = BeautifulSoup(pageTree.content, 'html.parser')

    return pageSoup

def extract_league_urls(pageSoup):
    urlSoup = pageSoup.find_all('table', {'class': 'inline-table'})
    leagueUrls = []

    for url in urlSoup:
        leagueUrls.append(
            BASE_URL + url.find_all('td')[1].find('a')['href']
        )

    return leagueUrls
    
def extract_club_urls(pageSoup):
    urlSoup = pageSoup.find('table', {'class': 'items'}).find_all('a', {'class': 'vereinprofil_tooltip'})
    clubUrls = set()

    for url in urlSoup:
        clubUrls.add(
            BASE_URL + url['href']
        )

    return clubUrls

def extract_players_info(pageSoup):
    playerSoup = pageSoup.find_all('tr', {'class': ['odd', 'even']})
    playersInfo = []

    for player in playerSoup:
        playersInfo.append({
            'name': player.find_all('a', {'class': 'spielprofil_tooltip'})[0].text,
            'position': player.find_all('td')[4].text,
            'number' : player.find_all('div', {'class': 'rn_nummer'})[0].text,
            'market_value': player.find_all('td', {'class': 'rechts hauptlink'})[0].text.split('€')[0] + '€', 
            'age': player.find_all('td', {'class': 'zentriert'})[1].text.split(' ')[1].replace('(', '').replace(')', ''),
            'date_of_birth': player.find_all('td', {'class': 'zentriert'})[1].text.split(' ')[0],
            'nation': player.find_all('img', {'class': 'flaggenrahmen'})[0]['title'],
            'contract_expires': player.find_all('td', {'class': 'zentriert'})[3].text.replace('.', '/')
        })
    
    return playersInfo

def extract_manager_info(pageSoup):
    managerSoup = pageSoup.find('div', {'class': 'container-inhalt'})

    confuseString = managerSoup.find('div', {'class': 'container-zusatzinfo'}).text

    confuseString = confuseString.split(':')
    age = confuseString[1].split(' ')[1]
    since = confuseString[2].split('\t')[0].replace(' ', '')
    contractExpires = confuseString[3].split('\t')[0].replace(' ', '').replace('.', '/')

    managerInfo = {
        'name': managerSoup.find('a').text,
        'nation': managerSoup.find('img')['alt'],
        'age': age,
        'contract_expires': contractExpires,
        'since': since,
    }

    return managerInfo

def extract_club_info(pageSoup):
    clubSoup = pageSoup.find_all('span', {'class': 'dataValue'})

    clubInfo = {
        'name': pageSoup.find('h1').text.replace('\n', '').replace(' ', ''),
        'amount_of_players': clubSoup[0].text.replace('\n', '').replace(' ', ''),
        'media_age': clubSoup[1].text.replace('\n', '').replace(' ', ''),
        'market_value': pageSoup.find('div', {'class': 'dataMarktwert'}).find('a').text.replace(' Valor de mercado total', ''),
        'manager': extract_manager_info(pageSoup)
    }

    detailPageUrl = BASE_URL + pageSoup.find('div', {'class': 'table-footer'}).find('a')['href']
    detailSoup = make_request(detailPageUrl)

    print('CLUB -> ', clubInfo['name'])
    clubInfo['players'] = extract_players_info(detailSoup)

    return clubInfo

def extract_league_info(pageSoup):
    leagueSoup = pageSoup.find_all('table', {'class': 'profilheader'})[0].find_all('td')

    leagueInfo = {
        'name': pageSoup.find('h1', {'class': 'spielername-profil'}).text,
        'nation': leagueSoup[0].find('img')['alt'],
        'amount_of_clubs': leagueSoup[1].text.replace('\n', '').replace(' ', '').replace('Equipas', ''),
        'amount_of_players': leagueSoup[2].text.replace('\n', '').replace(' ', ''),
        'market_value': pageSoup.find('div', {'class': 'marktwert'}).find('a').text
    }

    clubUrls = extract_club_urls(pageSoup)
    clubsInfo = []

    n = len(clubUrls)
    i = 0
    print('\n\n\nLEAGUE -> ', leagueInfo['name'], '\n')
    print('0 of ', n, 'CLUBS scrapped')
    for url in clubUrls:
        clubsInfo.append(
            extract_club_info(
                make_request(url)
            )
        )
        i += 1
        print(i, ' of ', n, 'CLUBS scrapped')
        time.sleep(5)


    leagueInfo['clubs'] = clubsInfo

    return leagueInfo


if __name__ == "__main__":
    print('\n\nInicializando...\n\n')
    baseSoup = make_request(page)
    leagueUrls = extract_league_urls(baseSoup)
    
    leaguesInfo = []

    n = len(leagueUrls)
    i = 0
    print('0 of ', n, 'LEAGUES scrapped')
    for leagueUrl in leagueUrls:
        leagueSoup = make_request(leagueUrl)
        leaguesInfo.append(extract_league_info(leagueSoup))
        i += 1
        print('\n\n', i, ' of ', n, 'LEAGUES scrapped')

        time.sleep(5)

    with open('personal.json', 'w') as json_file:  
        json.dump(leaguesInfo, json_file)
