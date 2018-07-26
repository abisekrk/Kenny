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
changeMargin=[]


def generate_csv_files():
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
"""
def predict_mean(resultSet):
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

    return geometricMeanOfFuture
"""

def predict_mean(resultSet):
	totalDays=len(resultSet)
	x_train=[[i] for i in range(0,totalDays)]
	y_train=resultSet[0:totalDays]
	reg=linear_model.LinearRegression()
	reg.fit(x_train,y_train)
	x_test=[[i] for i in range(totalDays,totalDays+10)]
	y_predicted=reg.predict(x_test)
	predictedDB.append(y_predicted)
	geometricMeanOfFuture=scistats.gmean(y_predicted)
	return geometricMeanOfFuture
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
    diff= (geometricMeanOfFuture-resultSet[-1])/resultSet[-1]

  

    return diff


def find_change_margins(stocks):
    #This function uses predict_stock_prices funtion to simply
    #find the mean of predicted values in next 10 days for all the
    #available stocks.
    
    for i in stocks:
        print(i)
        resultSet=dba_fetch_prices(i,1000)
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

    #If a stock has rank 5 , and the chnage margin is positive you should buy it!
     if (stockRank[stocks.index(symbol)] ==5 ) and (changeMarginDB[stocks.index(symbol)]>0):
        return True
     else:
        return False


def find_balance_price(username):
	import sqlite3 as database

	db= database.connect("stocks.sqlite")
	iterator= db.cursor()
	iterator.execute("select balance from users where userId='"+username+"'")
	temp=iterator.fetchall()[0][0]
	return temp;
   

def update_global_table(moneyLeft,s,username):
	import sqlite3 as database
	db= database.connect("stocks.sqlite")
	iterator= db.cursor()


	stocksBought= int(moneyLeft/dba_fetch_prices(s,1)[0]  )

	print("Alreay bought: "+str(stocksBought))
	stockDetailFetch= "select "+s+" from global_portfolio "
			
	iterator.execute(stockDetailFetch)
			
	stocksInTable= iterator.fetchall()[0][0]
	insertInTable=stocksInTable+stocksBought
	updateGlobal = "update global_portfolio set "+s+" = "+str(insertInTable)
	iterator.execute(updateGlobal)

	db.commit()
	db.close()
	if stocksBought>0:
		update_user_table(username,stocksBought,stocksInTable,insertInTable,s)
	return stocksBought

def update_user_table(username,stocksBought,stocksInTable,insertInTable,s):
	import sqlite3 as database
	db= database.connect("stocks.sqlite")
	iterator= db.cursor()

	dataOfUser= "select * from "+username+" where stockName= '"+s+"'"
	print(dataOfUser)
	iterator.execute(dataOfUser)
	temp= iterator.fetchall()
	print(len(temp))
	noOfStocks=temp[0][1]
	avgSpent= temp[0][2]
	print("No of stocks: "+str(noOfStocks)+" and avgSpent: "+ str(avgSpent))

	toBeUpdateValue= ((noOfStocks*avgSpent) + (stocksBought* dba_fetch_prices(s,1)[0] )) / insertInTable
	deleteUser="delete from "+username+" where stockName= '"+s+"'"
	iterator.execute(deleteUser)
	updateUser= "insert into "+username+" values ('"+s+"',"+str(insertInTable)+","+str(toBeUpdateValue)+")"
	iterator.execute(updateUser)
	print("I have bought "+str(stocksBought))
	db.commit()
	db.close()

def buy_a_particular_stock(s,moneyLeft,username):
	

	print(" I am buying : "+s)
	print("\nLast day Price: "+str(  dba_fetch_prices(s,1)[0] ))

	stocksBought=update_global_table(moneyLeft,s,username)
	

	
	
	moneyLeft-=stocksBought*dba_fetch_prices(s,1)[0]
	return moneyLeft	


def buy_stock(username):
	
	import sqlite3 as database
	db= database.connect("stocks.sqlite")
	iterator= db.cursor()

	moneyLeft=find_balance_price(username)
	for s in stocks:
		if should_you_buy(s):
			moneyLeft=buy_a_particular_stock(s,moneyLeft,username)
			
	iterator.execute("update users set balance="+str(moneyLeft)+ " where userId='"+username+"'")
	db.commit()
	db.close()


def dba_new_stock(stockName):
	#cREATING a tABLE fOR tHE nEWLY aDDED sTOCK
	import sqlite3 as database
	#establish connection,i'm assuming one table per stock,stockname==tablename
	db=database.connect("stocks.sqlite")
	#then update
	iterator=db.cursor()
	#not sure abput thus sql_command part
	sql_command="create table if not exists "+stockName+"(price float)"
	iterator.execute(sql_command)
	iterator.execute("create table if not exists global_portfolio(id int primary key)")
	sql_command="alter table global_portfolio add "+stockName+" int"
	iterator.execute(sql_command)
	db.commit()
	db.close()




def dba_fetch_prices(stockName,nDays):
	#fewtches prices of last nDays
	import sqlite3 as database
	#establish connection
	db=database.connect("stocks.sqlite")
	iterator=db.cursor()
	##fetching
	
	#alternative method
	sql_command="select price from "+stockName+" order by rowid desc limit "+str(nDays) 
	iterator.execute(sql_command)
	price=[i[0] for i in iterator.fetchall()]
	# because we used ascending
	price.reverse()
	
	return price


def dba_daily_push(stockName,todaysPrice):
	#i am importing the required libraries in the functions, makes porting easy apprently
	import sqlite3 as database

	#establish connection,i'm assuming one table per stock,stockname==tablename
	db=database.connect("stocks.sqlite")
	#then update	
	iterator=db.cursor()
	if(todaysPrice=="-"):
		todaysPrice=dba_fetch_prices(stockName,1)
		todaysPrice=str(todaysPrice[0])
	sql_command="insert into "+stockName+" values("+str(todaysPrice)+");"
	iterator.execute(sql_command)
	db.commit()
	db.close()

def initialise_all_tables(username):
	import sqlite3 as database
	db=database.connect("stocks.sqlite")
	iterator= db.cursor()
	
	initialise = "insert into global_portfolio values ( '"+username+"'"+(",0"*len(stocks))+")"
	iterator.execute(initialise)

	for s in stocks:
		#table_updater= "insert into "+username+" values('"+s+"'"+",0,0)"
		table_updater= "update "+username+" set numberOfStocks=0,amountSpent=0 where stockName='"+s+"'"
		iterator.execute(table_updater)

	db.commit()
	db.close()



def table_for_user(username):

	import sqlite3 as database
	db=database.connect("stocks.sqlite")
	iterator= db.cursor()

	cmd= "create table if not exists "+username+" (stockName varchar primary key,numberOfStocks int, amountSpent float)"
	iterator.execute(cmd)
	
	db.commit()
	db.close()

def update_today_stock_price():
	for s in stocks:

		toUpdateStockDetails = get_single_stock(stockDB,stocks,s) ;
		print(  type(toUpdateStockDetails));
		dba_new_stock(s);
		for price in toUpdateStockDetails:
			dba_daily_push(s,price);


def dba_getDetails(customerId):
	import sqlite3 as database
	db=database.connect("stocks.sqlite")
	iterator=db.cursor()
	iterator.execute("select * from "+customerId)
	stockDetails=[]
	for i in iterator.fetchall():
		stockDetails.append(i)
	db.close()
	return stockDetails

def sellOrWait(pricePerUnit,todaysPrice,predictedFuturePrice):
	profit_today=todaysPrice-pricePerUnit
	profit_wait=todaysPrice-predictedFuturePrice
	maxprofit=max(profit_wait,profit_today)
	#haven't implemented logic to foresee a crash and sell :(
	if(maxprofit>0):
		if(maxprofit==profit_today):
			return 1
	return 0

def add_balance(customerId,amount):
	import sqlite3 as database
	db=database.connect("stocks.sqlite")
	iterator=db.cursor()
	#>>>>>not sure about the tablename confirm with chan<<<<<<
	iterator.execute("update users set balance=balance+"+str(amount)+" where userId='"+customerId+"'")
	db.commit()
	db.close()	

def sell(customerId,stockName,noOfStock,pricePerUnit):
	# have to update the customer's own table
	import sqlite3 as database
	db=database.connect("stocks.sqlite")
	iterator=db.cursor()
	iterator.execute("update "+customerId+" set numberOfStocks=0, amountSpent=0 where stockName='"+stockName+"'")
	db.commit()
	db.close()
	#also have to update the global cash available table
	#->>>>>>>>>>>>please implement this<<<<<<<<<<<<<<<<<<<
	add_balance(customerId,noOfStock*pricePerUnit)
	#also have to update the global portfolio table 
	db=database.connect("stocks.sqlite")
	iterator=db.cursor()
	iterator.execute("update global_portfolio set "+stockName+"=0 where id='"+customerId+"'")
	db.commit()
	db.close()
	
def predictFuturePrice(stockName):

	resultSet= dba_fetch_prices(stockName,200)
	futurePrice= predict_mean(resultSet)
	return futurePrice
	
def sell_logic(customerId):
	#get stockName and price per stock from the table and put it as a pair in a list
	stockDetails=dba_getDetails(customerId)
	for i in stockDetails:
		stockName=i[0]
		noOfStock=i[1]
		pricePerUnit=i[2]
		todaysPrice=(dba_fetch_prices(stockName,1)[0])
		predictedFuturePrice=predictFuturePrice(stockName)#>>>>>>>>>>>>just a stub, Abisek<<<<<<<<<<<<<<
		if(stockName=="ATVI"):
			print(todaysPrice,predictedFuturePrice,pricePerUnit)
		if(sellOrWait(pricePerUnit,todaysPrice,predictedFuturePrice) ): #if it returns 1 imma gonna sell it today
			#print("selling "+stockName)
  			sell(customerId,stockName,noOfStock,todaysPrice)

def populate(username):

	for s in stocks:
		q="insert into "+username+" values ('"+s+"',0,0);"
		db_stuff(q)


#Have to do this daily to fetch data from Google finance
	# and load it to the database
	# Then the stocks in the db are ranked according to their predicted values
stockDB=get_from_csv(stocks)
changeMarginDB=find_change_margins(stocks)
minMaxStocks=findBestAndWorstStocks(changeMarginDB)
rank_the_stocks(changeMarginDB)

def db_stuff(sql):
	import sqlite3 as database
	db=database.connect("stocks.sqlite")
	iterator=db.cursor()
	iterator.execute(sql)
	db.commit()
	db.close()	

def db_delete():
	db_stuff("delete from global_portfolio;")
	#populate("customer102")
	initialise_all_tables("customer102")
	db_stuff("update customer102 set numberOfStocks=100,amountSpent=10 where stockName='ATVI';")
	db_stuff("update global_portfolio set ATVI=100")
	db_stuff("update users set balance=10000;")
'''

buy_stock("customer102")
#testing
sell_logic('rka')
'''
#show the output at each step
#add some money
	#front end addition
	#db_stuff("insert into users('');")
#table_for_user("customer102")
#populate("customer102")
##buy some stocks
#buy_stock('customer102')
#sell some stocks
#initialise_all_tables("customer102")
#sell_logic("customer102")



#To show
#db_delete()
#buy_stock('customer102')
sell_logic("customer102")
