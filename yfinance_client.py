#!/usr/bin/env python

from decimal import Decimal
from Queue import Queue
from threading import current_thread, Thread
import urllib
import json

__all__ = ['get_quotes', 'StockQuote']

NUM_SIMULTANEOUS_REQUESTS = 3

class StockQuote(object):
    def __init__(
        self, original_ticker, ticker, name, last, change,
        day_low, day_high, year_low, year_high,
        volume, average_daily_volume, market_cap
    ):
        self.original_ticker = original_ticker
        self.ticker = ticker
        self.name = name
        self.last = last
        self.change = change
        self.day_low = day_low
        self.day_high = day_high
        self.year_low = year_low
        self.year_high = year_high
        self.volume = volume
        self.average_daily_volume = average_daily_volume
        self.market_cap = market_cap
    
    @property
    def percent_change(self):
        return self.change / (self.last - self.change) * 100
    
    def __repr__(self):
        return "<StockQuote('%s'): %f" % (self.ticker, self.last)

class YRequester(object):
    ROOT_URL = 'http://query.yahooapis.com/v1/public/yql'

    def __init__(self, tickers):
        self.job_queue = Queue()
        self.results = []
        self.tickers = tickers
        self.ticker_map = dict([(self.make_yahoo_ticker(x), x) for x in tickers])
    
    @classmethod
    def get_chunks(self, l, n):
        while True:
            if len(l) < n:
                if len(l) > 0:
                    yield l
                break
            yield l[0:n]
            l = l[n:]

    @classmethod
    def make_yahoo_ticker(self, t):
        return t.replace('.', '-')

    def quotes_worker(self):
        while not self.job_queue.empty():
            chunk = self.job_queue.get()
            try:
                url = self.ROOT_URL + '?' + urllib.urlencode({
                    'format': 'json',
                    'env': 'store://datatables.org/alltableswithkeys',
                    'q': 'select * from yahoo.finance.quote where symbol in (%s)' % (
                        ','.join(['"%s"' % x for x in chunk])
                    )
                })
                
                # print("%s: %s" % (current_thread().name, url))
                res = json.load(urllib.urlopen(url))
                if 'query' not in res:
                    raise Exception("'query' not found in result: %s" % str(res))
                for s in res['query']['results']['quote']:
                    if s['StockExchange'] is None:
                        continue
                    self.results.append(StockQuote(
                        self.ticker_map[s['symbol']],
                        s['symbol'],
                        s['Name'],
                        Decimal(s['LastTradePriceOnly']),
                        Decimal(s['Change']),
                        Decimal(s['DaysLow']),
                        Decimal(s['DaysHigh']),
                        Decimal(s['YearLow']),
                        Decimal(s['YearHigh']),
                        long(s['Volume']),
                        long(s['AverageDailyVolume']),
                        s['MarketCapitalization'],
                    ))
            finally:
                self.job_queue.task_done()

    def get_quotes(self):
        for chunk in self.get_chunks(self.ticker_map.keys(), 100):
            self.job_queue.put(chunk)
        for i in range(NUM_SIMULTANEOUS_REQUESTS):
            t = Thread(target=self.quotes_worker)
            t.start()
        self.job_queue.join()
        out = {}
        for q in self.results:
            out[q.original_ticker] = q
        return out

def get_quotes(tickers):
    return YRequester(tickers).get_quotes()

if __name__ == '__main__':
    print(get_quotes(['AAPL', 'VNQ', 'SPY']))
