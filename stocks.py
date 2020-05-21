import os
import datetime

import yfinance as yf
from pymongo import MongoClient
import json

from dotenv import load_dotenv
load_dotenv()


def get_company_info(company):
    companyObject = {}

    companyInfo = yf.Ticker(company).info

    # setting fields in company object
    companyObject['name'] = companyInfo['shortName']
    companyObject['tickerSymbol'] = companyInfo['symbol']
    companyObject['sector'] = companyInfo['sector']
    companyObject['currency'] = companyInfo['currency']

    return companyObject


def format_data_into_json(data):
    # resetting data frame index (date was index column)
    data.reset_index(inplace=True)

    # renaming the columns to be compliant with mongo schema
    data = data.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adjusted",
        "Volume": "volume"
    })

    # convert date column from datetime to string (e. g. 2020-05-21)
    data['date'] = data['date'].dt.strftime('%Y-%m-%d')

    # json object of data
    dataJSON = data.to_json(orient='records')

    return json.loads(dataJSON)


if __name__ == '__main__':

    # -------------------- DATABASE CONNECTION ----------------------- #

    STOCKS_URI = os.environ.get("STOCKS_URI")

    # connect to database hosted on mongodb atlas
    client = MongoClient(STOCKS_URI)

    # connection to database stockbotics
    db = client.get_database('stockbotics')

    # collection
    stocks_collection = db.stocks
    companies_collection = db.companies

    # deleting all documents in collection
    stocks_collection.delete_many({})
    companies_collection.delete_many({})

    # ------------- GATHERING STOCK MARKET INFORMATION --------------- #

    # ticker symbols of wanted companies
    top20 = ['ADBE', 'BA', 'CMCSA', 'CSCO', 'CVX', 'PFE', 'MRK', 'DIS', 'XOM', 'T', 'INTC', 'BAC', 'MA', 'WMT', 'JPM',
             'FB', 'GOOGL', 'AMZN', 'AAPL', 'MSFT']
    top10 = ['T', 'INTC', 'BAC', 'MA', 'WMT', 'FB', 'GOOGL', 'AMZN', 'AAPL', 'MSFT']

    # company objects is list of objects to insert
    companyObjectsList = []

    # iterate over wanted companies
    for company in top10:
        # company object is the JSON to put into the mongo database
        companyObject = get_company_info(company)

        # inserting companies data into companies collection
        companies_collection.insert_one(companyObject)

        # tomorrow date and 5 years ago to get the right data
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        fiveYears = 365.25 * 5
        fiveYearsAgo = tomorrow - datetime.timedelta(days=fiveYears)

        # gathering information
        print('Downloading company: ', company)
        data = yf.download(company, start=fiveYearsAgo, end=tomorrow)

        dataJSON = format_data_into_json(data)
        companyObject['stocks'] = dataJSON

        companyObjectsList.append(companyObject)

    # inserting company objects into database stocks collection
    stocks_collection.insert_many(companyObjectsList)
