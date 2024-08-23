#!/bin/python
# ===========================================================
# Created By: Chien Dat Nguyen Dinh
# Organization: LifeRaft
# Department: R&D
# Purpose: Create Jira Filter
# Date: 2024/07/30
# ===========================================================

import json
import time
import os
import logging
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config.get('jql_queries'), config.get('filter_url'), config.get('sprint_url')
    else:
        logging.error("Configuration file not found!")
        raise FileNotFoundError("Configuration file not found!")

def setup_chrome_options():
    script_profile_path = os.path.join(os.path.expanduser('./'), '.autoJiraProfile')
    if not os.path.exists(script_profile_path):
        os.makedirs(script_profile_path)
    
    prefs = {"download.default_directory": os.path.abspath(".")}
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-data-dir={script_profile_path}")
    chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options

def go_to_jira(browser, logged_in, jira_url):
    # jira_url = filter_url if url_type == 'filter_url' else sprint_url
    try:
        browser.get(jira_url)
        logging.info(f"Navigated to {jira_url}")
        if not logged_in:
            try:
                login_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@href='/login.jsp']"))
                )
                if login_button:
                    input("Please log in to Jira and then press Enter here...")
                    browser.get(jira_url)
                else:
                    logging.info("Login not required")
            except:
                logging.info("Login not required or login button not found")

        # element = WebDriverWait(browser, 20).until(
        #         EC.element_to_be_clickable((By.XPATH, "//a[@externalid='directory.filters-v2.create-button']")))
        # element.click()
        # logging.info("Clicked Create Filter Button")
        # time.sleep(5)
        
        logged_in = True
    except Exception as e:
        logging.error(f"An error occurred during navigation and login: {e}")
        import traceback
        logging.error(traceback.format_exc())
        raise
    
    return logged_in

def create_and_export_filter(jql_query, browser):
    try:
        element = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@externalid='directory.filters-v2.create-button']")))
        element.click()
        logging.info("Clicked Create Filter Button")
        time.sleep(5)
        logging.info("Attempting to click on filter input:")
        jql_input = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'jql-editor-input')]")))
        
        jql_input.send_keys(Keys.CONTROL + "a")
        jql_input.send_keys(Keys.DELETE)
        jql_input.send_keys(jql_query)
        jql_input.send_keys(Keys.RETURN)
        logging.info("Entered JQL query")

        export_menu = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-testid,'action-export-issues')]")))
        export_menu.click()
        logging.info("Clicked the Export menu")
        export_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//span[text()='Export CSV (all fields)']]"))
        )
        export_button.click()
        logging.info("Clicked the Export CSV button")
        logging.info("CSV export initiated successfully!")
        time.sleep(5)
    except Exception as e:
        logging.error(f"An error occurred during filter creation and export: {e}")
        import traceback
        logging.error(traceback.format_exc())
        raise

def get_sprint_goal(browser, is_logged_in, jira_url):
    go_to_jira(browser, is_logged_in, jira_url)
    sprint_goal_element = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@data-testid,'header.title.container')]/following-sibling::div")))

    sprint_goal = sprint_goal_element.text
    logging.info(f"Sprint Goal: {sprint_goal}")

    with open('sprintgoal.txt', mode='w') as file:
        file.write(f"{sprint_goal}\n")
    logging.info("Sprint goal saved to sprintgoal.txt")

def getJQLResult(jql_query, browser, jira_url, is_logged_in):
    go_to_jira(browser, is_logged_in, jira_url)
    create_and_export_filter(jql_query, browser)

def main():
    setup_logging()
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Jira Filter Automation Script")
    parser.add_argument('--config', type=str, default='config.json', help='Path to the configuration file')
    parser.add_argument('--only_parse_epic', action='store_true', help='Only parse epics from the JQL queries')
    args = parser.parse_args()

    jql_queries, filter_url, sprint_url = load_config(args.config)
    chrome_options = setup_chrome_options()
    
    try:
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logging.info("Chrome started successfully")
    except Exception as e:
        logging.error(f"Error starting Chrome: {e}")
        import traceback
        logging.error(traceback.format_exc())
        raise

    try:
        is_logged_in = go_to_jira(browser, False, filter_url)

        if args.only_parse_epic:
            logging.info("Only parsing epics as per the --only_parse_epic flag")
            jql_queries = [query for query in jql_queries if 'epic' in query.lower()]  # Filter for epics only

        for jql_query in jql_queries:
            getJQLResult(jql_query, browser, filter_url, is_logged_in)
        
        get_sprint_goal(browser, is_logged_in, sprint_url)

    except Exception as e:
        logging.error(f"An error occurred during execution: {e}")
        import traceback
        logging.error(traceback.format_exc())

    finally:
        browser.quit()
        logging.info("Browser closed")

if __name__ == "__main__":
    main()
