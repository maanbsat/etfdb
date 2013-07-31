#!/usr/bin/env python

from decimal import Decimal
import urllib
from bs4 import BeautifulSoup

class ISharesLib(object):
    ROOT_URL = 'http://us.ishares.com/product_info/fund/holdings/%s.htm?periodCd=d'

    def __init__(self):
        pass
    
    @classmethod
    def get_etf(self, ticker):
        url = self.ROOT_URL % ticker
        pg = BeautifulSoup(urllib.urlopen(url))
        print(pg)
        tbl = pg.find('table', id='holdings-eq')
        if tbl is None:
            raise Exception("Holdings table not found")
        return tbl

if __name__ == '__main__':
    print(ISharesLib.get_etf('IVE'))