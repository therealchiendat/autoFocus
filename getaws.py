#!/bin/python
# ===========================================================
# Created By: Chien Dat Nguyen Dinh
# Organization: Introhive
# Department: R&D
# Purpose: AWS SSO Credential Scrape
# Date: 2021/12/15
# ===========================================================

import selenium
import os
import time
import requests
import subprocess
import platform
import clipboard
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import json
with open('secrets.json','r') as f:
      config = json.load(f)

r = requests.get('https://' + 'introhivesso.awsapps.com/start#/')

# URL Variables
login_url = 'https://introhivesso.awsapps.com/start#/'

# WebDriver Path for System
if platform.system() == ('Windows'):
    browser = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\chromedriver.exe")
elif platform.system() == ('Linux'):
    browser = webdriver.Chrome(executable_path='/home/chiendat/Drivers/Google/Chrome/chromedriver')
elif platform.system() == ('Darwin'):
    browser = webdriver.Chrome(executable_path='/Users/chiendat/Work/RealWork/devByMe/Driver/chromedriver')
else:
    print("Are you sure you have the Selenium Webdriver installed in the correct path?")

# Parent URL
browser.get(login_url)

time.sleep(7)

# Credentials NEEDS UNIT TEST
# XPATH //*[@id='identifierId']
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='identifierId']")))
element.send_keys(config['user']['name'])
print("Sending Username...")

# Click Next
# Next Button ID XPATH //*[@id='identifierNext']/div/button/span
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.ID, "identifierNext")))
element.click();
print("Clicking Next Button...")
time.sleep(2)

# Password Payload
# Password XPTAH //*[@id='password']
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='password']/div[1]/div/div[1]/input")))
element.send_keys(config['user']['password'])

# Click Next
# Next Button XPATH //*[@id='passwordNext']/div/button/div[2]
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.ID, "passwordNext")))
element.click();
print("Clicking Login Button...")
time.sleep(15)

# Authentication submit.click()
# For XPATH = //portal-application
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//portal-application[@id='app-03e8643328913682']")))
element.click();
print("Clicking Portal Application Button...")

# Sandbox - Toolkit Dev
# For XPATH = //portal-instance
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//portal-instance[@id='ins-7f9a6736930a3bd7']")))
element.click();
print("Clicking Sandbox - Toolkit Dev")

# Command line or programmatic access
# For XPATH = //a[@id='temp-credentials-button']
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@id='temp-credentials-button']")))
element.click();
print("Clicking Command line or programmatic access")

# Command line or programmatic access
# For XPATH = //hover-to-copy[@id='hover-copy-env']
element = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//hover-to-copy[@id='hover-copy-env']")))

element.click();
print("Copied Command line or programmatic access")

# Write to .aws/credentials
formattedClipboard = '\n'.join(clipboard.paste().split('\n')[1:])
print("Writing to AWS Creds file")
cli = os.path.join(os.path.expanduser('~'),'.aws/credentials')
awsCredsFile = open(cli,"w");
awsCredsFile.write('[default]\n' + formattedClipboard);
print("Done")

