from ib_insync import *

# Connect to TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Define a contract (Apple stock)
contract = Stock('AAPL', 'SMART', 'USD')

# Request historical daily bars (last 1 year)
data = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='1 Y',
    barSizeSetting='1 day',
    whatToShow='MIDPOINT',
    useRTH=True
)

# Convert to DataFrame
df = util.df(data)
print(df.head())

ib.disconnect()
