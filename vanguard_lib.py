#!/usr/bin/env python

from decimal import Decimal
import urllib, urllib2, cookielib
from bs4 import BeautifulSoup

class VanguardLib(object):
    def __init__(self):
        super(VanguardLib, self).__init__()
        self._cookies = cookielib.CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(self._cookies)
        )
    
    def _get_csrf_token(self, page):
        token = page.find('input', attrs={'name': 'ANTI_CSRF_TOKEN'})['value']
        return token
    
    def get_etf(self, ticker):
        # 1. open the website, grab the CSRF
        pg = BeautifulSoup(
            self._opener.open('https://institutional.vanguard.com/VGApp/iip/site/institutional/home?fromPage=portal'),
            "html.parser"
        )
        csrf = self._get_csrf_token(pg)
                
        # 2. do a search on the ticker
        pg = BeautifulSoup(self._opener.open(
            'https://institutional.vanguard.com/VGApp/iip/site/institutional/home',
            urllib.urlencode({
                'browseProductsForm:fundSearchButton': 'browseProductsForm:fundSearchButton',
                'cbd_ria': 'true',
                'browseProductsForm:fundSearchInput': ticker,
                'browseProductsForm:fundSearchInputSelected': '',
                'ANTI_CSRF_TOKEN': csrf,
                'browseProductsForm': 'browseProductsForm'
            })
        ), "html.parser")
        csrf = self._get_csrf_token(pg)
        fund_id = pg.find('meta', attrs={'name': 'FUND_ID'})['content']
        
        # 3. request the PCF
        req = urllib2.Request(
            'https://institutional.vanguard.com/VGApp/iip/site/institutional/investments/productDetails/portfolio/Portfolio.xhtml',
            urllib.urlencode({
                'cbdCompId': 'comp-portfolioForm:portfolioCompositionDataTable',
                'portfolioForm': 'portfolioForm',
                'portfolioForm:hiddenPCFButton': 'portfolioForm:hiddenPCFButton',
                'cbd_ria': 'true',
                'currentProduct': fund_id,
                'portfolioForm:myTabBox5B:state': '',
                'portfolioForm:characteristicsTabBox:state': '',
                'portfolioForm:findHoldingHiddenInput': 'false',
                'portfolioForm:compTabBox:state': '',
                'portfolioForm:hiddenPCFButton': 'portfolioForm:hiddenPCFButton',
                'portfolioForm:navBoxManagement:state': '',
                'ANTI_CSRF_TOKEN': csrf,
                'portfolioForm': 'portfolioForm'
            })
        )
        pg = BeautifulSoup(self._opener.open(req), "html.parser")
        #open('out.html', 'w').write(str(pg))
        # print(pg)
        
        # 4. parse
        tbl = pg.find('table', id='portfolioForm:portfolioCompositionDataTable')
        for row in tbl.find_all('tr'):
            if 'class' not in row.attrs or not ('wr' in row['class'] or 'ar' in row['class']):
                continue
            vals = row.find_all('td')
            ticker = str(vals[0].string)
            if len(ticker) < 1:
                continue
            yield (ticker, Decimal(vals[3].string.strip('%'))/100)

if __name__ == '__main__':
    for l in VanguardLib().get_etf('VNQ'):
        print(l)