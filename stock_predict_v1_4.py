import requests
from datetime import datetime,timedelta
import csv
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats as scistats
#Assigning the 25 selected stock symbols to the list

stocks= ["AAPL","NVDA","MSFT","FB","CMCSA","MU","CDNS","TSLA","CHTR","GOOGL","WBA","CTSH","AVGO","INTC","ATVI","GILD","NFLX","CSCO"]
stockDB=[]
predictedDB=[]
stockRank=[]


def generate_csv_files:
    #Now We need to specify the start and end dates. This is supposed to work actually!
    # But it is not working! It simply gets the last one years data, which isn't that bad!

    today = datetime.now()

    todaysDate= today.strftime('%d')
    todaysMonth=today.strftime('%b')
    todaysYear=today.strftime('%Y')

    period=10
    start= datetime.now()- timedelta(days=period)
    startDate= start.strftime('%d')
    startMonth=start.strftime('%b')
    startYear=start.strftime('%Y')

    #We are building an url here! If you type this url in your browser, you will have the csv file downloaded to downloads!
    #Here it will be downloaded to our pwd

    urlPart1="http://www.google.com/finance/historical?q="
    urlPart2="&startdate="+startMonth+"+"+startDate+"%2C"+startYear+"&enddate="+todaysMonth+"+"+todaysDate+"%2C"+todaysYear+"&output=csv"

    #These lines create a new csv file in the name of the stock symbol and write the downloaded data!
    for s in stocks:
        url = urlPart1+s+urlPart2
        r = requests.get(url, allow_redirects=True)
        open(s+'.csv', 'wb').write(r.content)


def get_from_csv(stocks):
    #Now we have too many details in our csv file, but we only need the date and the prices!
    #So lets read from the csv file and store it locally in a list, which we will put into the DB soon!


    #We are creating a 3d list.
    #List's first dimension holds one year data of the 20 symbols
    #list's second dimension holds one year data of the symbol
    # List's third dimension holds one date and its corresponding price

    stockDB=[]
    for s in stocks:
        stockData = []
        with open(s+'.csv', 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader :
                mylist=[]
                mylist.append(row[0])
                mylist.append(row[1])
                stockData.append(mylist[:])

        stockDB.append(stockData[:])
    return stockDB



def get_single_stock(stockDB,stocks,stockSymbol):
    #This function gets a stocksymbol as input an0d return its stock prices for
    #that period as a single list.
    try:
        index=stocks.index(stockSymbol)
    except:
        print("Invalid stock details!")
        return
    resultSet=[]
    for i in range(1,len(stockDB[index])):
        resultSet.append(float(stockDB[index][i][1]))
    return resultSet

def predict_stock_prices(resultSet):

    #This function gives the entire dataset available for 
    #linear regression to train itself and asks to predict values
    #for next 10 days.

    totalDays=len(resultSet)
    
    x_train=[[i] for i in range(0,totalDays)]
    y_train=resultSet[0:totalDays]
    
    reg=linear_model.LinearRegression()
    reg.fit(x_train,y_train)
    
    x_test=[[i] for i in range(totalDays,totalDays+10)]    
    y_predicted=reg.predict(x_test)
    
    predictedDB.append(y_predicted)

    #Finding the geometric mean of the 10 predicted values
    geometricMeanOfFuture=scistats.gmean(y_predicted)
    

    #Find the difference of predicted mean vs last day value
    diff= geometricMeanOfFuture-resultSet[-1]
  

    return diff

def plot_graph():
    plt.scatter(x_learn, y_learn,  color='black')
    plt.plot(x_learn, y_pred, color='blue', linewidth=3)
    plt.xticks(())
    plt.yticks(())
    plt.show()


def find_change_margins(stocks):
    #This function uses predict_stock_prices funtion to simply
    #find the mean of predicted values in next 10 days for all the
    #available stocks.
    changeMargin=[]
    for i in stocks:
        print(i)
        resultSet=get_single_stock(stockDB,stocks,i)
        print(predict_stock_prices(resultSet))
        changeMargin.append( predict_stock_prices(resultSet))
        
    return changeMargin

def findBestAndWorstStocks(changes):
    #This function returns the stocks with largest and smallest , value
    #which is the mean value predicted for next 10 days.
    minMax=[]
    minMax.append(changes.index(max(changes)))
    minMax.append(changes.index(min(changes)))
    return minMax

def rank_the_stocks(changes):

    #This function ranks the stocks from 1 to 5
    #Rank 5 indicates that the stock is a must buy

    #The ranking strategy is:
        #-> Count the number of stocks whose mean values is less than the current stock
        # -> Now we will have a count of how many stocks, our current stock outweighs
        # -> If current stock weighs more than 80 % of other stocks, it gets rank 5
        # -> 60 % - Rank 4
        # -> 40% - Rank 3
        # -> 20% - Rank 2
        # -> Less than that - Rank 1

    for s in stocks:
        stockIndex= stocks.index(s)
        count=0
        for i in changes:
            if changes[stockIndex]>i:
                count+=1

        margin=[0.8*len(stocks),0.6*len(stocks),0.4*len(stocks),0.2*len(stocks)]
       
        flag=False

        for i in range (0, len(margin) ):
            if count>margin[i]:
                stockRank.append(5-i)
                flag=True
                break
        if not flag:
            stockRank.append(1)

       
def should_you_buy(symbol):

    #If a stock has rank 5 , you should buy it!
     if stockRank[stocks.index(symbol)] ==5:
        return True
     else:
        return False


def should_you_sell(symbol):

    #If a stock has rank 1, you should sell it!
    if(stockRank[stocks.index(symbol)])==1:
        return True
    else:
        return False

   

stockDB=get_from_csv(stocks)
changeMarginDB=find_change_margins(stocks)
minMaxStocks=findBestAndWorstStocks(changeMarginDB)
rank_the_stocks(changeMarginDB)