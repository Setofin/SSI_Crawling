# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:49:29 2020

@author: admin
"""
import pandas as pd
import numpy as np
import time
from selenium import webdriver
import datetime

from py_vollib.black_scholes.implied_volatility import implied_volatility 
from py_vollib.black_scholes import black_scholes 
import re
import seaborn as sns
import matplotlib.pyplot as plt


risk_free = 0.032
driver = webdriver.Chrome('C:\ChromeDriver\chromedriver')
current_day = datetime.date.today()
columns = ['Ticker', 'Issuer', 'Days', 'Matched_price', 'Matched_vol', 'Change', 'Pct_change', 'Symbol', 'Price', 'Excercise', 'Basis', 'CVN', 'Breakeven']

def get_df():
    return pd.read_csv('./Vn30.csv')

def get_volatility(ticker, data):
    df = data[data['Ticker'] == ticker]
    df['Risk'] = (df.Close / 1000).rolling(80).std()
    return df.Risk.iloc[-1]

def load_page():
    stock_url = 'https://iboard.ssi.com.vn/bang-gia/chung-quyen'
    driver.get(stock_url)
    time.sleep(6)
    
def crawl_cw():
    cw_table = driver.find_elements_by_xpath('//*[@id="table-table-scroll"]')
    cw_data = cw_table[0].find_elements_by_tag_name('tr')
    
    cw_crawled = []
    
    for data in cw_data:
        cw_row = data.find_elements_by_tag_name('td')
        cw_row_data = []
        for i in range(len(cw_row)):
            if (i <= 2) |(i >= 12) & (i <= 15)| (i >= 24):
                cw_row_data.append(cw_row[i].text) 
            
        cw_crawled.append(cw_row_data)
        
    driver.close()
    return pd.DataFrame(cw_crawled, columns = columns)
    
def get_iv(row):
    try:
        return implied_volatility(row.Matched_price * row.CVN, row.Price, row.Excercise ,row.Date / 360, risk_free, 'c')
    except:
        return np.nan

def get_price(row):
    try:
        return round(black_scholes('c',row.Price, row.Excercise, row.Date / 360, risk_free, get_volatility(row.Symbol, price_df)),3)
    except:
        return np.nan

price_df = get_df()

load_page()
dataframe = crawl_cw()
dataframe['Days'] = pd.to_datetime(dataframe['Days'])

dataframe['Date'] = (dataframe['Days'] - pd.to_datetime(current_day)).dt.days
#dataframe['Date'] = (dataframe.Date / np.timedelta64(1, 'D')).astype(int)

dataframe['Price'] = pd.to_numeric(dataframe['Price'])
dataframe['CVN'] = dataframe['CVN'].apply(lambda cvn : re.findall("([^:]+)",cvn)[0])
dataframe['CVN'] = pd.to_numeric(dataframe['CVN'])
dataframe['Excercise'] = pd.to_numeric(dataframe['Excercise'])
dataframe['Matched_price']= pd.to_numeric(dataframe['Matched_price'])
dataframe['Option_price'] = dataframe.apply(lambda row: get_price(row), axis = 1) 
dataframe['IV'] = dataframe.apply(lambda row: get_iv(row), axis = 1) 
dataframe['Price_deviation'] = dataframe['Matched_price'] * dataframe.CVN - dataframe['Option_price'] 
dataframe = dataframe.sort_values(by = ['IV', 'Price_deviation'], ascending = True)

print(dataframe)