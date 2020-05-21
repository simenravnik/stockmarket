# Stockmarket script

Script that downloads historical stock market data and store it in the database.

Create `.env` file and put your mongodb URI inside

Example `.env` file:

```
STOCKS_URI="mongodb+srv://<username>:<password>@stockbotics-1tv8w.mongodb.net/test?retryWrites=true&w=majority"
```

> NOTE: replace with your URI

## Install

```
pip install -r requirements.txt
```

## Start

```
python3 stocks.py
```