#!/usr/bin/env python

from flask import Flask, redirect, url_for, render_template
from etflib import get_etf_component_quotes

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for('etf_page', ticker='SPY'))

@app.route("/etf/<ticker>")
def etf_page(ticker):
    ticker = ticker.upper()
    res = get_etf_component_quotes(ticker)
    return render_template('etf_page.html', components=res)

if __name__ == "__main__":
    app.run(debug=True, port=5005)