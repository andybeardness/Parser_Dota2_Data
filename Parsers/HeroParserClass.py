import requests
from bs4 import BeautifulSoup

import pandas as pd

class HeroParser:
    def __init__(self):
        self.DOTABUFF_LINK = 'https://ru.dotabuff.com' 
        self.HEROES_LINK = 'https://ru.dotabuff.com/heroes'

        self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        
        self.data = {
            'name' : [],
            'href' : [],
            'wrate': [],
        }
        
        self.dataNameHrefWinrate = None
        self.dataMatrixWinRate   = None
        
    def parse_NameHrefWinrate(self):
        source = requests.get(url     = self.HEROES_LINK,
                              headers = self.HEADERS)
        
        soup = BeautifulSoup(source.text)
        
        hrefs = soup.find('div', class_='hero-grid').find_all('a')
        for href in hrefs:
            self.data['href'].append(href.get('href'))
            
        names = soup.find_all('div', class_='name')
        for name in names:
            self.data['name'].append(name.get_text())
            
        for href in self.data['href']:
            hero_link = self.DOTABUFF_LINK + href
            hero_source = requests.get(url     = hero_link,
                                       headers = self.HEADERS)

            hero_soup = BeautifulSoup(hero_source.text)

            won_lost = hero_soup.find('span', class_='won')

            if won_lost is not None:
                item = won_lost.get_text().replace('%', '')
            else:
                item = hero_soup.find('span', class_='lost').get_text().replace('%', '')

            item = float(item)
            self.data['wrate'].append(item)
            
        self.dataNameHrefWinrate = pd.DataFrame(self.data)
        
    def parse_MatrixWinRate(self):
        self.dataMatrixWinRate = pd.DataFrame(columns=self.data['name'], index=self.data['name'])
        
        for href in self.data['href']:
            current_hero = self.dataNameHrefWinrate[self.dataNameHrefWinrate['href'] == href]['name']
            current_link = self.DOTABUFF_LINK + href + '/counters'
            current_source = requests.get(url     = current_link,
                                          headers = self.HEADERS)

            current_soup = BeautifulSoup(current_source.text)

            current_table = current_soup.find('table', class_='sortable').find('tbody').find_all('tr')

            for item in current_table:
                hero_name  = item.find_all('td')[0].get('data-value')
                hero_wrate = float(item.find_all('td')[3].get('data-value'))

                self.dataMatrixWinRate.loc[current_hero, hero_name] = hero_wrate
        
        for col in self.dataMatrixWinRate.columns:
            self.dataMatrixWinRate[col] = self.dataMatrixWinRate[col].astype('float') 
        
        self.dataMatrixWinRate = self.dataMatrixWinRate.fillna(0)
                
    def save_files(self, path='../Data/Heroes/', names=['dataNameHrefWinrate.csv', 'dataMatrixWinRate.csv']):
        self.dataNameHrefWinrate.to_csv(f'{path}{names[0]}', index=False)
        self.dataMatrixWinRate.to_csv(f'{path}{names[1]}')