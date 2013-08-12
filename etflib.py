#!/usr/bin/env python

import re
import urllib
from bs4 import BeautifulSoup
from spdrs_lib import SPDRSLib
from vanguard_lib import VanguardLib
from yfinance_client import get_quotes

def get_etf_client_lib(ticker):
    pg = urllib.urlopen('http://finance.yahoo.com/q/pr?s=%s+Profile' % ticker)
    pg = BeautifulSoup(pg)
    txt = re.compile('Fund Family')
    family = pg.find(text=txt).parent.next_sibling.text
    if 'SPDR' in family:
        return SPDRSLib
    elif 'Vanguard' in family:
        return VanguardLib
    raise Exception("Don't know how to deal with '%s' ETF" % family)

def get_etf_component_quotes(ticker):
    components = list(get_etf_client_lib(ticker)().get_etf(ticker))
    #print(components)
    res = get_quotes([x[0] for x in components])
    for (ticker, weight) in components:
        if ticker not in res:
            continue
        res[ticker].weight = weight
    return res

if __name__ == '__main__':
    print(get_etf_component_quotes('SPY'))
