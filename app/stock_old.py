from app import app
from app.dynamo import dynamodb

from flask import request, render_template, redirect, url_for, session, g
import json
from boto3.dynamodb.conditions import Key, Attr
from yahoo_finance import Share





@app.route('/get_quote_old')
def stock_quote_get_old():
    table = dynamodb.Table('Stocks')

    print(str(request))
    symbol = str(request.args.get('symbol'))
    year = str(request.args.get('year'))
    month = str(request.args.get('month'))
    day = str(request.args.get('day'))
    print('year: ' + year + '\n' + 'month: ' + month + '\n' + 'day: ' + day + '\n')
    date = year + '-' + month + '-' + day

    yahoo = Share(symbol)
    yahoo_quote = yahoo.get_historical(date, date) # should return list with a single dict item
    quote = {
        'symbol': yahoo_quote[0]['Symbol'],
        'date': yahoo_quote[0]['Date'],
        'open': yahoo_quote[0]['Open'],
        'high': yahoo_quote[0]['High'],
        'low': yahoo_quote[0]['Low'],
        'close': yahoo_quote[0]['Close'],
        'volume': yahoo_quote[0]['Volume'],
    }

    #response = table.get_item(
    #    Key={
    #        'stock': ticker,
    #        'date': date
    #    },
    #    ProjectionExpression="date, open, high, low, close, volume"
    #    #ExpressionAttributeNames={"#dt": "date"}
    #)

    #data = {}

    #if 'Item' in response:
     #   item = response['Item']
     #   data.update(item)

    return render_template("stock/stock_detail_old.html", stock=quote)

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

@app.route('/stock_price_history')
def stock_price_history():
    table = dynamodb.Table('Stocks')

    year = int(request.args.get('year'))
    title_from = request.args.get('title_from')
    title_to = request.args.get('title_to')

    response = table.query(
        ProjectionExpression="#yr, title, rating",
        ExpressionAttributeNames={"#yr": "year"},  # Expression Attribute Names for Projection Expression only.
        KeyConditionExpression=Key('year').eq(year) & Key('title').between(title_from, title_to)
    )

    records = []

    for i in response['Items']:
        records.append(i)

    return render_template("stock/stocks.html", stocks=records)


@app.route('/put')
def stock_put():
    table = dynamodb.Table('Stocks')

    title = request.args.get('title')
    year = int(request.args.get('year'))
    rating = request.args.get('rating')

    response = table.put_item(
        Item={
            'year': year,
            'title': title,
            'plot': "Nothing happens at all.",
            'rating': rating
        }
    )

    return redirect(url_for('index'))


@app.route('/update')
def stock_update():
    table = dynamodb.Table('Stocks')

    title = request.args.get('title')
    year = int(request.args.get('year'))
    rating = request.args.get('rating')

    response = table.update_item(
        Key={
            'year': year,
            'title': title
        },
        UpdateExpression="set rating = :r, plot=:p, actors=:a",
        ExpressionAttributeValues={
            ':r': rating,
            ':p': "Everything happens all at once.",
            ':a': ["Larry", "Moe", "Curly"]
        }

    )

    return redirect(url_for('index'))


@app.route('/import_data')
def import_data():
    table = dynamodb.Table('Stocks')

    with open("stockdata.json") as json_file:
        stocks = json.load(json_file)
        for stock in stocks:
            year = int(stock['year'])
            title = stock['title']
            info = stock['info']

            print("Adding stock:", year, title)

            item = {
                'year': year,
                'title': title
            }

            item.update(info)

            table.put_item(
                Item=item
            )

    return redirect(url_for('index'))


@app.route('/list_all')
def list_all():
    table = dynamodb.Table('Stocks')

    fe = Key('year').between(1950, 1959);
    pe = "#yr, title, rating"
    # Expression Attribute Names for Projection Expression only.
    ean = {"#yr": "year", }
    esk = None

    # FilterExpression=fe,

    response = table.scan(
        ProjectionExpression=pe,
        ExpressionAttributeNames=ean
    )

    records = []

    for i in response['Items']:
        records.append(i)

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression=pe,
            ExpressionAttributeNames=ean,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )

        for i in response['Items']:
            records.append(i)

    return render_template("stock/stocks.html", stocks=records)


@app.route('/stocks')
def stocks_year():
    table = dynamodb.Table('Stocks')

    if 'year' not in request.args or \
                    request.args.get('year').isdigit() == False:
        return "Error! All inputs most be of type int"

    year = int(request.args.get('year'))

    response = table.query(
        KeyConditionExpression=Key('year').eq(year)
    )

    records = []

    for i in response['Items']:
        records.append(i)

    return render_template("stock/stocks.html", stocks=records)


@app.route('/stocks_year_title')
def stocks_year_title():
    table = dynamodb.Table('Stocks')

    year = int(request.args.get('year'))
    title_from = request.args.get('title_from')
    title_to = request.args.get('title_to')

    response = table.query(
        ProjectionExpression="#yr, title, rating",
        ExpressionAttributeNames={"#yr": "year"},  # Expression Attribute Names for Projection Expression only.
        KeyConditionExpression=Key('year').eq(year) & Key('title').between(title_from, title_to)
    )

    records = []

    for i in response['Items']:
        records.append(i)

    return render_template("stock/stocks.html", stocks=records)
