#!/usr/bin/env python

from spdrs_lib import SPDRSLib
from yfinance_client import get_quotes

def get_etf_client_lib(ticker):
    return SPDRSLib

def get_etf_component_quotes(ticker):
    components = list(get_etf_client_lib(ticker).get_etf(ticker))
    #print(components)
    res = get_quotes([x[0] for x in components])
    for (ticker, weight) in components:
        if ticker not in res:
            continue
        res[ticker].weight = weight
    return res

if __name__ == '__main__':
    print(get_etf_component_quotes('SPY'))
