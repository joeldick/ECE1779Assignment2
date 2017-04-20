from app import app
from app.dynamo import dynamodb

from flask import request, render_template, redirect, url_for, session, g
import json
from boto3.dynamodb.conditions import Key, Attr
from yahoo_finance import Share
from datetime import date, datetime
import time


@app.route('/get_quote', methods=['GET'])
def stock_quote_get():
    print(request.args.get('symbol'))
    symbol = str(request.args.get('symbol'))

    # get all the relevant data from the Yahoo Finance API
    stock = Share(symbol)

    stock_name = stock.get_name()
    stock_symbol = stock.symbol
    stock_price = stock.get_price()
    stock_change = stock.get_change()
    stock_change_pct = stock.get_percent_change()

    prev_close = stock.get_prev_close()
    open = stock.get_open()
    day_range = stock.get_days_range()
    year_range = stock.get_year_range()
    volume = stock.get_volume()
    avg_volume = stock.get_avg_daily_volume()
    market_cap = stock.get_market_cap()
    pe_ratio = stock.get_price_earnings_ratio()
    eps = stock.get_earnings_share()
    dividend = stock.get_dividend_share()
    dividend_yld = stock.get_dividend_yield()
    dividend_ex_date = stock.get_ex_dividend_date()
    yr_target = stock.get_one_yr_target_price()

    historical = stock.get_historical('2017-01-01', date.isoformat(date.today()))

    # put the data into the DynamoDB database
    table = dynamodb.Table('Stocks')
    response = table.put_item(
        Item={
            'symbol': symbol,
            'date': date.isoformat(date.today()),
            'prev_close': prev_close,
            'open': open,
            'day_range': day_range,
            'year_range': year_range,
            'volume': volume,
            'avg_volume': avg_volume,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'eps': eps,
            'dividend': dividend,
            'dividend_yld': dividend_yld,
            'dividend_ex_date': dividend_ex_date,
            'yr_target': yr_target,
        }
    )

    close_history = []

    for point in historical:
        close_date = point['Date']
        close_date = int(time.mktime(datetime.strptime(close_date, "%Y-%m-%d").timetuple()))
        close_price = point['Adj_Close']
        close_price = float(close_price)
        close_history.append([close_date, close_price])

    return render_template("stock/stock_detail.html",
                           stock_name=stock_name,
                           stock_symbol=stock_symbol,
                           stock_price=stock_price,
                           stock_change=stock_change,
                           stock_change_pct=stock_change_pct,
                           prev_close=prev_close,
                           open=open,
                           day_range=day_range,
                           year_range=year_range,
                           volume=volume,
                           avg_volume=avg_volume,
                           market_cap=market_cap,
                           pe_ratio=pe_ratio,
                           eps=eps,
                           dividend=dividend,
                           dividend_yld=dividend_yld,
                           dividend_ex_date=dividend_ex_date,
                           yr_target=yr_target,
                           close_history=close_history
                           )


@app.route('/get_quote_detail/<id>', methods=["GET"])
def get_quote_detail(id):
    stock = Share(id)

    historical = stock.get_historical('2017-01-01', date.isoformat(date.today()))

    close_history = []

    for point in historical:
        close_date = point['Date']
        # close_date = datetime.strptime(close_date, '%Y-%m-%d')
        close_price = point['Adj_Close']
        close_price = float(close_price)
        close_history.append([close_date, close_price])

    return render_template("stock/stock_detail_history.html",
                           close_history=close_history,
                           symbol=id
                           )


@app.route('/stock_compare', methods=["GET", "POST"])
def stock_compare():
    if request.method == 'GET':

        return render_template("stock/stock_compare_form.html")

    elif request.method == 'POST':

        print(request.form.get('symbol1'))
        print(request.form.get('symbol2'))
        print(request.form.get('symbol3'))
        print(request.form.get('symbol4'))
        print(request.form.get('symbol5'))

        symbol1 = str(request.form.get('symbol1'))
        symbol2 = str(request.form.get('symbol2'))
        symbol3 = str(request.form.get('symbol3'))
        symbol4 = str(request.form.get('symbol4'))
        symbol5 = str(request.form.get('symbol5'))
        symbols = [symbol1,symbol2,symbol3,symbol4,symbol5]

        stocks = []
        for symbol in symbols:
            stocks.append(Share(symbol))

        close_histories = []
        for stock in stocks:
            historical = stock.get_historical('2017-01-01', date.isoformat(date.today()))

            close_history = []

            for point in historical:
                close_date = point['Date']
                close_date = int(time.mktime(datetime.strptime(close_date, "%Y-%m-%d").timetuple()))
                close_price = point['Adj_Close']
                close_price = float(close_price)
                close_history.append([close_date, close_price])
            close_histories.append(close_history) # list of lists

        # todo change stock_compare.html template so it has a graph with five lines
        return render_template("stock/stock_compare.html",
                               close_histories=close_histories,
                               symbols=symbols
                               )

        # return render_template("stock/stock_compare.html",
        #                   close_history=close_history,
        #                   symbol=id
        #                   )

        ## The Functions below are all leftovers from the movies database.
        ## Update for stocks with functions that do the following:
        ## (Note: all data is passed in through the request variable using either GET or POST
        ##  and all functions end calling a html template to render the data returned for the user.)
        ## 1. Update table: User specifies a stock symbol, a start date, and an end date.
        ##    Function call the yahoo finance API to get historical data, and loads it into
        ##    the databse.
        ## 2. Get historical data: User specifies a stock symbol.
        ##    Function queries the database and then returns all historical closing prices.
        ## 3. Get current quote/details: User specifies a stock symbol.
        ##    Function calls yahoo finance API and returns current information about the stock:
        ##    i.e. get_name(), get_info(), get_price(), get_change(), previous close, open,
        ##    bid, ask, volume, market cap, beta, PE Ratio, EPS, Dividend, Yield, 1y estimate
        ##    and template should format it nicely.
