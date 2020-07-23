from bs4 import BeautifulSoup
from requests import get
import sqlite3
from sys import argv
from terminaltables import AsciiTable

URL = 'https://www.olx.pl/motoryzacja/samochody/renault/q-renault-talisman/'


def parse_price(price_to_parse):
    return float(price_to_parse.replace(' ', '').replace('zł', '').replace(',', ''))


def get_offers(table):
    last_page = int(
        BeautifulSoup(get(URL).content, features='html.parser').find(attrs={'data-cy': 'page-link-last'}).get_text())
    offer_table = [
        ['Name', 'Price', 'Location']
    ]
    for page in range(1, last_page + 1):
        page_content = get(f'{URL}?page={page}')
        bs = BeautifulSoup(page_content.content, features='html.parser')
        for offer in bs.find_all('div', class_='offer-wrapper'):
            link = offer.find('a')['href']
            footer = offer.find('td', class_='bottom-cell')
            location = footer.find('small', class_='breadcrumb').get_text().strip()
            name = offer.find("strong").get_text().strip()
            price = parse_price(offer.find("p", class_="price").get_text().strip())
            if table:
                offer_table.append([name, price, location])
            else:
                cursor.execute('SELECT * FROM offers WHERE link=?', (link,))
                in_db = cursor.fetchone()
                if not in_db:
                    cursor.execute('INSERT INTO offers VALUES (?, ?, ?, ?)', (name, price, location, link))
        print(f"Loading... Done {page/last_page*100}%")
    if table:
        ascii_table = AsciiTable(offer_table)
        print(ascii_table.table)
    else:
        conn.commit()


if len(argv) > 1:
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    if '--create-db' in argv:
        cursor.execute('CREATE TABLE offers (name TEXT, price REAL, location TEXT, link TEXT)')
        quit()
    elif '--update-db' in argv:
        get_offers(False)
        conn.close()
else:
    get_offers(True)

