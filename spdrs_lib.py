#!/usr/bin/env python

from decimal import Decimal
import urllib
from xlrd import open_workbook

class SPDRSLib(object):
    URL = 'https://www.spdrs.com/site-content/xls/SPY_All_Holdings.xls?fund=SPY&docname=All+Holdings&onyx_code1=1286&onyx_code2=1700'

    def __init__(self):
        pass
    
    @classmethod
    def get_etf(self, ticker):
        url = self.URL
        wb = open_workbook(file_contents=urllib.urlopen(url).read())
        sheet = wb.sheet_by_index(0)
        for l in range(5, sheet.nrows):
            ticker = sheet.cell(l, 1).value.strip()
            if len(ticker) < 1:
                continue
            yield (ticker, Decimal(sheet.cell(l, 2).value)/100)

if __name__ == '__main__':
    for r in enumerate(SPDRSLib.get_etf('SPY')):
        print(r)