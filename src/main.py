#!/usr/bin/python3.5
# -*- coding: utf8 -*-
# Script for parcing Russian Dissertation Data
# Source:
# Destination: CSV file
#
# Python 3.5
# Concerting the http://docs.python-guide.org/en/latest/writing/style/
#
#
# CREDITS:
# Author: Ilya Rusin <franchb@protonmail.ch>
# Sergey Saltykov <sergey.saltykov@gmail.com>
#
# @Ageism Dev Team
# Created on 10 September 2016
##
##
# Code License: MIT
##
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities
from bs4 import BeautifulSoup
import pandas as pd
# import datetime as dt
from json import dumps

# Main OpenDisser Scraper

#Constants
URL_DOMAIN = 'https://teacode.com/online/vak/'
URL_FIRST_PAGE = ''
CSV_DIR = 'csv/'
CSV_FNAME = 'categories-'

# Function to ask yes/no
def q_yn(q, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(q + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

# Function to wait Web Driver on specific page
# returns 0 if OK and 1 if there was an error

def wait_pageload(w):
    try:
        WebDriverWait(w, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'OntoBox.org')))
    except:
        return 1
    return 0

def parse_diss_text(dtext):
    return dtext

def get_clist(w, url=URL_DOMAIN):
    w.get(url)
    wait_pageload(w)
    print('Page %s is loaded' % url)

    bsObj = BeautifulSoup(w.page_source, "lxml")

    ptable = bsObj.html.body.table.table

    if 'Паспорт специальности' in bsObj.title.string:
        a = ptable.tbody.find_all("tr")[1].td.html
        a = parse_diss_text(a)
        dh = bsObj.html.body.table.tbody.tr.td
        ztable = [[dh.h1.text,dh.h3.text,url,a]]
    else:
        ztable = [([a.text for a in row.find_all("td")] +
                [URL_DOMAIN + j['href'] for j in row.find_all("a", href=True)]+[''])
                for row in ptable.find('tbody').find_all("tr", recursive=False)][1:-1]

    return ztable


def recurse_urls(w):

    def gc(c, n=2):
        return [x[n] for x in c]

    p = get_clist(w)
    
    for i in gc(p):
        j = get_clist(w,i)
        p += j
        if gc(j,3)[0]=='':
            print(p)
            for ii in gc(j):
                jj = get_clist(w,ii)
                p += jj
                if gc(jj,3)[0]=='':
                    print(p)
                    for iii in gc(jj):
                        jjj = get_clist(w, iii)
                        p += jjj
                        if gc(jjj,3)[0]=='':
                            print(p)
                            for iiii in gc(jjj):
                                print(iiii)

    columns = ['code', 'name', 'url', 'text']

    df = pd.DataFrame(p,columns=columns)

    return df

########
# Main code


# Set HTTP Headers following the Ethical Web Scraping Practice
# Note: site administrators stay healthy when our bot looks like a human

# Code snippet from @andriy-ivaneyko on StackOverflow
desired_capabilities = DesiredCapabilities.CHROME.copy()

desired_capabilities['chrome.page.customHeaders.Accept'] = '*/*'
desired_capabilities['chrome.page.customHeaders.Accept-Encoding'] = 'gzip, deflate, sdch'
desired_capabilities['chrome.page.customHeaders.Accept-Language'] = 'ru-RU,en;q=0.8'
desired_capabilities['chrome.page.customHeaders.Cache-Control'] = 'max-age=0'
desired_capabilities['chrome.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/79.0.3945.79 Chrome/79.0.3945.79 Safari/537.36'

w = webdriver.Chrome(desired_capabilities=desired_capabilities)

ps = q_yn(
    'Perform new Categories parsing? (It will take about 10 minutes)', default='no')

if ps:
    p = recurse_urls(w)
    
    csv_name = CSV_DIR + CSV_FNAME + '-latest.csv'
    json_name = CSV_DIR + CSV_FNAME + '-latest.json'
    
    p.to_csv(csv_name, header=True)
    # @see https://pandas-docs.github.io/pandas-docs-travis/reference/api/pandas.DataFrame.to_json.html#pandas.DataFrame.to_json
    p.to_json(json_name, force_ascii=false, orient='records')
else:
     print('Nothing has been made. Good bye!')

w.quit()