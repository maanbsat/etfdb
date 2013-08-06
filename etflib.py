#!/usr/bin/env python

from spdrs_lib import SPDRSLib
from yfinance_client import get_quotes_iter

def get_etf_client_lib(ticker):
    return SPDRSLib

def get_etf_component_quotes(ticker):
    components = get_etf_client_lib(ticker).get_etf(ticker)
    res = get_quotes_iter([x[0] for x in components])
    return res

if __name__ == '__main__':
    print(get_etf_component_quotes('SPY'))
