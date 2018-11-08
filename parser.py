from selenium import webdriver
from bs4 import BeautifulSoup
import re
import config
import copy
import pickle
import os


def get_html(url):
    """Получение html-страницы"""
    driver = webdriver.PhantomJS()
    driver.get(url)
    html = driver.page_source
    return html


def get_instruments():
    """Получение базы инструментов"""
    html = get_html(config.URL_INSTRUMENTS)
    soup = BeautifulSoup(html, 'lxml')
    instruments = []
    table = soup.find('table', {'class': 'db-product'})
    for row in table.find_all('tr')[2:]:
        cols = row.find_all('td')
        instruments.append({
            'id': cols[1].contents[0],
            'name': cols[2].contents[0],
            'delivery': cols[3].contents[0]})
    return instruments


def check_instrument(text):
    """Проверка инструмента на наличие в базе"""
    instruments = get_instruments()
    for instrument in instruments:
        if instrument['id'] == text:
            return True


<<<<<<< HEAD
def check(html):
    """Проверка на завершение торгов"""
=======
def check():
    """Проверка на завершение торгов"""
    html = get_html(config.URL_TRADES)
>>>>>>> 8fbb20598c3c1c0167ba2ee90ee41d1fbe2e4f00
    soup = BeautifulSoup(html, 'lxml')
    fin = soup.find('tfoot')
    try:
        finish = list(map(lambda x: x.text.strip(), fin.find_all('td')[1:5:3]))
        if finish[0] == '—' and finish[1]:
            return True
    except:
        return False

        
def parse_table(html, instrument):
    """Парсинг таблицы с торгами"""
    soup = BeautifulSoup(html, 'lxml')
    for table in soup_html.find_all('table', {'id': '_table'}):
        for row in table.find_all('tr', {'id': instrument}):
            cols = row.find_all('td')
            try:
                name = cols[0].a.text
            except:
                name = ''
            try:
                offer_price = int(cols[1].find('span', {'class': 'red'}).text.replace(u'\xa0', ''))
            except:
                offer_price = ''
            try:
                offer_height = cols[1].find('span', {'class': 'gray'}).text.replace(u'\xa0', '')
            except:
                offer_height = ''
            try:                
                demand_price = int(cols[3].find('span', {'class': 'green'}).text.replace(u'\xa0', ''))
            except:
                demand_price = ''
            try:
                demand_height = cols[3].find('span', {'class': 'gray'}).text.replace(u'\xa0', '')
            except:
                demand_height = ''
            try:
                price = int(cols[4].contents[0].replace(u'\xa0', '').strip())
            except:
                price = ''
            try:
                contract_m = int(cols[5].contents[0].replace(u'\xa0', '').replace(u'р.', '').strip())
            except:
                contract_m = ''
            try:
                contract_height = int(cols[5].find('span', {'class': 'gray'}).text.replace(u'\xa0', '').replace(u'т.', '')) 
            except:
                contract_height = ''
            try:
                amount = int(cols[6].text.strip())
            except:
                amount = ''
            data = {
                'name': name,
                'offer_price': offer_price,
                'offer_height': offer_height,
                'demand_price': demand_price,
                'demand_height': demand_height,
                'price': price,
                'contract_m': contract_m,
                'contract_height': contract_height,
                'amount': amount}
    return data

    
def get_diff(currents):
    """Получение текущих и предыдущих данных"""
    if currents:
        if os.path.exists('temp'):
            previous = copy.copy(currents)
            os.remove('temp')
        else:
            with open('previous', 'rb') as f:
                previous = pickle.load(f)   
        with open('previous', 'wb') as f:
            pickle.dump(currents, f)    
    return currents, previous


def get_msg(item, name, price, height):
    """Получение информации о ходе торгов"""
    if item == 'offer_price':
        text = 'появилось предложение'
    elif item == 'demand_price':
        text = 'появился спрос'
    elif item == 'contract':
        text = 'ПРОИЗОШЛА!!! СДЕЛКА!!!'
    msg = (
        "На бирже {} на: {} "
        "по цене: {}р. "
        "в объеме: {}".format(
            text,
            name,
            price,
            height))
    return msg


def get_info(cur, prev):
    """Получение информации о ходе торгов"""
    result = []
    name = cur['name']
    if cur['offer_price'] != prev['offer_price']:
            result.append(get_msg('offer_price', name, cur['offer_price'], cur['offer_height']))
    if cur['demand_price'] != prev['demand_price']:
            result.append(get_msg('demand_price', name, cur['demand_price'], cur['demand_height']))
    with open('price.txt', a) as f:
        if cur['amount'] == 1:
            result.append(get_msg('contract', name, cur['price'], cur['contract_height']))
            f.write(str(cur['price']) + ';')
        if cur['amount'] > 1 and cur['contract_m'] != prev['contract_m']:
            cur_contract_height = cur['contract_height'] - prev['contract_height']
            cur_price = int((cur['contract_m'] - prev['contract_m']) / cur_contract_height)
            result.append(get_msg('contract', name, cur_price, cur_contract_height))
            f.write(str(cur_price) + ';')
    return result       


def get_report(html, instrument):
    """Получение отчета по завершению торгов"""
    if check(html):
        totals = parse_table(soup, instrument)
        with open('price.txt', 'r') as f:
            prices = f.read().split(';')
        res = list(map(int, prices))
        last_price = prices[-1]
        report = (
            "Итоги торгов: на {} "
            "было совершено сделок: {}  "
            "в объеме: {} т. "
            "по средней цене: {} р. "
            "самая низкая цена: {} р. "
            "самая высокая цена: {} р. "
            "последня цена: {} р".format(
                totals['name'],
                totals['amount'],
                totals['contract_height'],
                totals['price'],
                str(min(res)),
                str(max(res)),
                prices[-1]))
        return report 

        
def rotate_files():
    """Удаление и создание файлов"""
    if not os.path.exists('temp'):
        os.mknod('temp')
    if os.path.exists('previous'):
        os.remove('previous')