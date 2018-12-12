import requests
import json
import time
import pandas as pd

TOTAL_SENTIMENT_SCORE = 'total_sentiment_score'
TOTAL_REVIEW_COUNT = 'total_review_count'
SUM_STOCK_PRICE = 'sum_stock_price'
AVG_STOCK_PRICE = 'avg_stock_price'
TOTAL_DAYS = 'total_days'
DATE = 'date'
POLARITY_SCORE =  "polarity_score"
AVG_SCORE = 'avg_score'
LAST_DATE = '2014-10'
CLOSING_PRICE = 'Closing Price'
CLOSE = 'close'
AVG_SENTIMENT = 'Avg. Sentiment'
PERCENT_CHANGE = 'Percent Change'
STOCK_PERCENT = 'Stock % change'
SENTIMENT_PERCENT = 'Sentiment % change'

COMPANY_STOCK_SYMBOLS = {
    "Square":"SQ",
    "Etsy":"ETSY",
    "Netflix":"NFLX",
    "Ulta":"ULTA",
    "Workday":"WDAY",
    "Shopify":"SHOP",
    "Paypal": "PYPL",
    "Apple":"AAPL",
    "Facebook":"FB",
    "Lululemon":"LULU",
    "Grubhub":"GRUB"
}

# given the dictionary of all the glassdoor reviews for a company, and the last_review_date we want
# we will build a dictionary where each key is the date and the value is a dictionary that holds the overall sentiment score & total review count
def get_monthly_sentiment_dict(company_reviews, last_review_date):

    monthy_sentiment_dict = {}

    for review_id in company_reviews:
        date = company_reviews[review_id][DATE][:-3]
        if date < last_review_date and len(monthy_sentiment_dict) > 20:   # if we passed the last month/year to collect, stop
            break

        if date not in monthy_sentiment_dict:
            monthy_sentiment_dict[date] = {}
            monthy_sentiment_dict[date][TOTAL_SENTIMENT_SCORE] = 0
            monthy_sentiment_dict[date][TOTAL_REVIEW_COUNT] = 0

        monthy_sentiment_dict[date][TOTAL_SENTIMENT_SCORE] += company_reviews[review_id][POLARITY_SCORE]
        monthy_sentiment_dict[date][TOTAL_REVIEW_COUNT]+=1

    return monthy_sentiment_dict


# calculates the avg sentiment for each month and adds it to the original dict
# and returns a new dict of just the monthly sentiment score (i.e. key = date, value = avg_monthly_sentiment)
def get_monthly_avg_sentiment(company_monthly_sentiment_dict):

    monthly_scores = {}
    for date in company_monthly_sentiment_dict:
        avg_score = company_monthly_sentiment_dict[date][TOTAL_SENTIMENT_SCORE]/ company_monthly_sentiment_dict[date][TOTAL_REVIEW_COUNT]
        company_monthly_sentiment_dict[date][AVG_SCORE] = avg_score
        monthly_scores[date] = avg_score

    return monthly_scores

# takes in the company name, and last_date tuple (year, month) and returns a dict containing the monthly closing price for each company
# formatted such that key = (year, month), value = closing price
def get_company_monthly_close(company_name, last_date):

    print('CURRENTLY ON COMPANY: ',  company_name)
    time.sleep(15) # throttle to avoid Alpha Vantage API call limit -- 5 calls / min

    API_KEY = ""
    REQUEST_URL_BASE = "https://www.alphavantage.co/query"
    payload = {'function': 'TIME_SERIES_MONTHLY', 'apikey':API_KEY}

    if company_name == 'PayPal': company_name = 'Paypal' # small hiccup, when creating Paypal's dict in phase 1 there's a typo

    payload['symbol'] = COMPANY_STOCK_SYMBOLS[company_name]
    r = requests.get(REQUEST_URL_BASE, params=payload)
    company_stock_data = r.json()
    monthly_closing_data = company_stock_data['Monthly Time Series']
    result = {}

    for month in monthly_closing_data:
        date = month[:-3]
        if date < last_date: break
        if date == '2018-12': continue
        closing_price = monthly_closing_data[month]['4. close']
        result[date] = float(closing_price)

    return result

def init():

    # stores the avg monthly sentiment for each company -- a dict of dict.
    # where each company has a dict, such that key = (year, month), value = monthly avg sentiment

    sc_avg_monthly_sentiment = {} # 'small companies avg monthly sentiment'
    lc_avg_monthly_sentiment = {} # 'large companies avg monthly sentiment'

    sc_monthly_stock_close = {} # ' small companies monthly closing stock price'
    lc_monthly_stock_close = {} # 'large companies monthly closing stock price'

    with open('small_company_reviews_polarity_scores.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    small_company_reviews = json.loads(data)

    with open('large_company_reviews_polarity_scores.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    large_company_reviews = json.loads(data)

    for group in [small_company_reviews, large_company_reviews]:
        for c in group:
            company_dict = get_monthly_sentiment_dict(group[c],LAST_DATE)
            company_monthly_sentiment_avg = get_monthly_avg_sentiment(company_dict)
            closing_stock_prices = get_company_monthly_close(c, LAST_DATE)

            if group == small_company_reviews:
                sc_avg_monthly_sentiment[c] = company_monthly_sentiment_avg
                sc_monthly_stock_close[c] = closing_stock_prices
            else:
                lc_avg_monthly_sentiment[c] = company_monthly_sentiment_avg
                lc_monthly_stock_close[c] = closing_stock_prices

    # write the stock and company info to txt files

    f1 = open("large_company_monthly_sentiment.txt", "w+")
    f1.write(json.dumps(lc_avg_monthly_sentiment))
    f1.close()

    f1 = open("small_company_monthly_sentiment.txt", "w+")
    f1.write(json.dumps(sc_avg_monthly_sentiment))
    f1.close()

    f1 = open("large_company_monthly_stocks.txt", "w+")
    f1.write(json.dumps(lc_monthly_stock_close))
    f1.close()

    f1 = open("small_company_monthly_stocks.txt", "w+")
    f1.write(json.dumps(sc_monthly_stock_close))
    f1.close()


# helper function to format the key for the previous month
def get_previous_month(month_string):
    # "2014-0X" -- when the month is a single digit, 0 goes in front

    year = int(month_string[:4])
    month = int(month_string[-2:])
    month -=1
    result = ''

    if month == 0:
        month = 12
        year -=1

    result+=(str(year))
    result+='-'

    if month < 10:
        result+=('0'+str(month))
    else:
        result+=(str(month))

    return result


def get_percent_change(a, b):
    return (a-b) / b

# returns a dataframe with the percentage change for closing price and avg sentiment for a company
def get_graph_coord(monthly_prices, monthly_sentiment):

    sentiment_coord = {}
    stock_coord = {}

    for month in monthly_sentiment:
        if month == "2014-10": break # we won't calculate the percent change for the last day

        # need to format to get the previous month (key)
        previous_month = get_previous_month(month)

        if previous_month not in monthly_prices or previous_month not in monthly_sentiment:
            continue
        # calculate the percent change for both stock and sentiment
        stock_current_month = monthly_prices[month]
        stock_previous_month = monthly_prices[previous_month]
        stock_percent_diff = get_percent_change(stock_current_month, stock_previous_month)

        sentiment_current_month = monthly_sentiment[month]
        sentiment_previous_month = monthly_sentiment[previous_month]
        sentiment_percent_diff = get_percent_change(sentiment_current_month, sentiment_previous_month)

        # update the dictionaries

        sentiment_coord[month] = sentiment_percent_diff
        stock_coord[month] = stock_percent_diff

    stocks_df = pd.DataFrame(stock_coord, index=[STOCK_PERCENT])
    stocks_df = stocks_df.T

    sentiment_df = pd.DataFrame(sentiment_coord, index=[SENTIMENT_PERCENT])
    sentiment_df = sentiment_df.T

    stocks_df[SENTIMENT_PERCENT] = sentiment_df[SENTIMENT_PERCENT]
    correlation = stocks_df[STOCK_PERCENT].corr(stocks_df[SENTIMENT_PERCENT])


    print('Correlation: ', correlation)
    print(' ')
    return (sentiment_coord, stock_coord)


# given the dictionary of monthly closing stock prices and monthly avg sentiment scores for a company,
# returns the correlation between the two (a value between -1 to 1)
def get_df_correlation(monthly_prices, monthly_sentiment):

    prices_df = pd.DataFrame(monthly_prices, index=[CLOSING_PRICE])
    prices_df = prices_df.T # transpose row / cols

    sentiment_df = pd.DataFrame(monthly_sentiment, index=[AVG_SENTIMENT])
    sentiment_df = sentiment_df.T

    prices_df[AVG_SENTIMENT] = sentiment_df[AVG_SENTIMENT]
    correlation = prices_df[AVG_SENTIMENT].corr(prices_df[CLOSING_PRICE])

    return prices_df



# instead of doing the analysis based on the month's closing stock price... let's do the comparison on the moving average
def get_company_moving_avg(company_name):

    time.sleep(2)

    if company_name == 'PayPal': company_name = 'Paypal'  # small hiccup, when creating Paypal's dict in phase 1 there's a typo
    REQUEST_URL = "https://api.iextrading.com/1.0/stock/" + COMPANY_STOCK_SYMBOLS[company_name]  + "/chart/5y"

    r = requests.get(REQUEST_URL)
    daily_stock_data = r.json()

    historical_prices = {} # dictionary that keeps track of the total sum of stocks and number of days per month, to calculate the monthly average


    for entry in daily_stock_data:
        date = entry[DATE][:-3]
        if date < LAST_DATE or date in ['2018-12']:
            continue

        if date not in historical_prices:
            historical_prices[date] = {}
            historical_prices[date][TOTAL_DAYS] = 0
            historical_prices[date][SUM_STOCK_PRICE] = 0

        historical_prices[date][SUM_STOCK_PRICE]+= entry[CLOSE]
        historical_prices[date][TOTAL_DAYS]+=1

    # now calculate the monthly average
    average_monthly_stock = {}
    for month in historical_prices:
        average_monthly_stock[month]= historical_prices[month][SUM_STOCK_PRICE] / historical_prices[month][TOTAL_DAYS]

    return average_monthly_stock



# gets the correlation between stock prices and avg sentiment each month for all companies
def get_all_companies_correlation():

    with open('small_company_monthly_sentiment.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    small_company_sentiment = json.loads(data)

    with open('small_company_monthly_stocks.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    small_company_stocks = json.loads(data)

    with open('large_company_monthly_sentiment.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    large_company_sentiment = json.loads(data)

    with open('large_company_monthly_stocks.txt', 'r') as myfile:
        data = myfile.read()
    myfile.close()
    large_company_stocks = json.loads(data)


    for group in [small_company_stocks, large_company_stocks]:
        for c in group:
            print(c)
            average_monthly_stock_price = get_company_moving_avg(c)
            if group == small_company_stocks:
                get_df_correlation(small_company_stocks[c], small_company_sentiment[c])
                get_graph_coord(average_monthly_stock_price, small_company_sentiment[c])
            else:
                get_graph_coord(average_monthly_stock_price, large_company_sentiment[c])
                get_df_correlation(large_company_stocks[c], large_company_sentiment[c])

    return

# get_all_companies_correlation()


# BASED ON PERCENT CHANGE AND MOVING AVERAGE

# Square
# -0.01048908912523195
#
# Lululemon
# -0.05607332389134671
#
# Workday
# 0.1196661421525131
#
# Etsy
# -0.1433104768673486
#
# Shopify
# 0.5499292645088557
#
# Grubhub
# -0.2045696903435296
#
# Netflix
# 0.04660470405883612
#
# PayPal
# 0.001125894949762557
#
# Ulta
# -0.008774692916692296
#
# Facebook
# 0.20941687636012443
#
# Apple
# -0.09990978186930763