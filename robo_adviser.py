#I used the code that we worked through in class and then worked with Jaclyn Dornfeld

import csv
from dotenv import load_dotenv
import json
import os
import pdb
import requests
import datetime

def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="db/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)

if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests
    api_key = "6VMGWJEMD59KTB2O"
    print(api_key)
    # CAPTURE USER INPUTS (SYMBOL)
    # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS
    while True:
        symbol = str(input("Please input a stock symbol (e.g. 'NFLX'): "))
        if not symbol.isalpha():
            while True:
                yeah = input("If you are sure this symbol contains numbers, type 'Y'.  ")
                if yeah.lower() == "y":
                    print("OK, Processing....")
                    break
                else:
                    print("Ok Bye!")
                    quit()
        # ASSEMBLE REQUEST URL
        request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol + "&apikey=" + api_key
        response = requests.get(request_url)


        if "Error Message" in response.text:
            print("REQUEST ERROR, PLEASE TRY AGAIN. CHECK YOUR SYMBOL.")
        else:
            print("Thank you for entering your symbol.")
            break

    daily_prices = parse_response(response.text)

    print("Date / Time Program was Executed: ", datetime.datetime.now().strftime("%m-%d-%y %H:%M"))
    latest_date_refresh = daily_prices[0]["date"]
    print("Data was Refreshed On:  " + latest_date_refresh)
    latest_closing_price = daily_prices[0]["close"]
    latest_closing_price = float(latest_closing_price)
    latest_recent_average_high_price = 0
    j = 0
    for i in daily_prices:
        latest_recent_average_high_price += float(i["high"])
        j += 1
    latest_recent_average_high_price = latest_recent_average_high_price/j
    latest_recent_average_low_price = 0
    j = 0
    for i in daily_prices:
        latest_recent_average_low_price += float(i["low"])
        j += 1
    latest_recent_average_low_price = latest_recent_average_low_price/j
    #reccomendation
    range = latest_recent_average_high_price - latest_recent_average_low_price
    recommend_price = range * .5 + latest_recent_average_low_price
    if latest_closing_price < recommend_price:
        j = 1
    else:
        j = 2

    #converting variables to the proper format and printing
    latest_closing_price = "${0:,.2f}".format(latest_closing_price)
    latest_recent_average_high_price = "${0:,.2f}".format(latest_recent_average_high_price)
    latest_recent_average_low_price = "${0:,.2f}".format(latest_recent_average_low_price)
    print("Latest Closing Price:   " + latest_closing_price)
    print("Recent Average Low Price:   " + latest_recent_average_low_price)
    print("Recent Average High Price:   " + latest_recent_average_high_price)
    if j == 1:
        print("I feel like this stock is gonna start going up soon. Let's buy!")
    elif j == 2:
        print("I feel like this stock is not going to go much higher. Let's not buy.")

    # WRITE TO CSV
    write_prices_to_file(prices=daily_prices, filename="db/prices.csv")
