# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 14:08:31 2020

@author: admin
"""

import pandas as pd
import numpy as np
import time
from selenium import webdriver
import datetime

import re
import seaborn as sns
import matplotlib.pyplot as plt

driver = webdriver.Chrome('C:\ChromeDriver\chromedriver')

def load_page():
    stock_url = 'https://iboard.ssi.com.vn/bang-gia/vn30'
    driver.get(stock_url)
    time.sleep(6)
    
load_page()

tbody_load = driver.find_elements_by_xpath('//*[@id="table-body-scroll"]')
tr_load = tbody_load[0].find_elements_by_tag_name('tr')

data = []

for tr in tr_load:
    ticker = tr.find_elements_by_class_name('stockSymbol.txt-down')
    fbuy = tr.find_elements_by_class_name('buyForeignQtty.txt-normal')
    fsell = tr.find_elements_by_class_name('sellForeignQtty.txt-normal')
    froom = tr.find_elements_by_class_name('remainForeignQtty.txt-normal')
    
    try:
        data.append((ticker[0].text, fbuy[0].text, fsell[0].text, froom[0].text))
    except:
        continue
    

fdata = pd.DataFrame(data, columns = ['Ticker','Fbuy', 'Fsell','Froom'])
print(fdata.head())
driver.close()