import requests
from time import sleep
import os
from bs4 import BeautifulSoup as bs
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import re
import sys

folderSlice = '/'
if sys.platform == 'windows':
    folderSlice = '\\'

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

se = requests.Session()

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.214 Safari/537.36'
}

def get(url):
        sleep(0.1)
        resp = se.get(url=url, headers=headers, verify=False, timeout=10)
        if resp.status_code == 200:
            return resp.content
        else:
            return None

def run(pageNumber=1):
    maxPage = None
    while True:
        print(f'Page: {pageNumber}')
        if maxPage and pageNumber > maxPage:
            print('All pages loaded. Exit')
            break
        resp = get(f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber={pageNumber}&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz223=on&fz44=on&af=on&ca=on&pc=on&pa=on&currencyIdGeneral=-1')
        soup = bs(resp, 'html.parser')
        pagination = soup.find('ul', attrs= {'class' : 'pages'}).findAll('span')[-1].text
        if pagination:
            maxPage = int(pagination)
        entries = soup.find_all('div', attrs = {'class' : 'search-registry-entry-block'})

        for entry in entries:
            title = entry.select('.registry-entry__header-top__title')[0].text
            link = entry.select('.registry-entry__header-mid__number a')[0]['href']
            print(link)
            if '44-ФЗ' in title:
                ext = 'html'
                regNumber = re.search(r'regNumber=(\d+)', link)[1]
                if os.path.exists(folderSlice.join([regNumber, 'printform.html'])):
                    print(f'Document {folderSlice.join([regNumber, "printform.html"])} already exist. Skip...')
                    continue
                printTitle = entry.select('.registry-entry__header-top__icon a')[-1]['href']
                printNumber = re.search(r'regNumber=(\d+)', printTitle)[1]
                printLink = f'https://zakupki.gov.ru/epz/order/notice/printForm/view.html?regNumber={printNumber}'
                data = get(printLink)
                
                
            elif '223-ФЗ' in title:
                ext = 'xml'
                regNumber = re.search(r'noticeInfoId=(\d+)', link)[1]
                if os.path.exists(folderSlice.join([regNumber, 'printform.xml'])):
                    print(f'Document {folderSlice.join([regNumber, "printform.xml"])} already exist. Skip...')
                    continue
                printTitle = entry.select('.registry-entry__header-top__icon a')[-1]['href']
                printNumber = re.search(r'noticeId=(\d+)', printTitle)[1]
                
                printLink = f'https://zakupki.gov.ru/223/purchase/public/notification/print-form/show.html?noticeId={printNumber}'
                resp = get(printLink)
                printPage = bs(resp, 'html.parser')
                data = printPage.select('#tabs-2')[0].text
            if not os.path.exists(regNumber):
                os.makedirs(regNumber, exist_ok=True)
            with open(folderSlice.join([regNumber, 'printform.'+ ext]), ext == 'xml' and 'wt' or 'wb') as f:
                print(f'Save to : {folderSlice.join([regNumber, "printform."+ ext])}')
                f.write(data)
        pageNumber += 1

run()

se.close()