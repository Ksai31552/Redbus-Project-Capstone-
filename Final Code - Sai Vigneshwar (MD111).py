# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 19:01:55 2024

@author: Sai.Vigneshwar
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException, StaleElementReferenceException
from sqlalchemy import create_engine
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URLS = [
    'https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/astc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc/?utm_source=rtchometile',
    'https://www.redbus.in/online-booking/wbtc-ctc/?utm_source=rtchometile',
]
WAIT_TIME = 10
GOV_BUS_NAMES = ["TSRTC", "APSRTC", "KSRTC", "SBSTC", "WBTC", "HRTC", "RSRTC", "ASTC"] # try removing Buses

def extract_data_from_page(driver):
    wait = WebDriverWait(driver, WAIT_TIME)
    route_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.route_link')))
    data = []
    
    for route_element in route_elements:
        try:
            route_link_element = route_element.find_element(By.CSS_SELECTOR, 'a.route')
            route = route_link_element.text
            link = route_link_element.get_attribute('href')
            fare = route_element.find_element(By.CSS_SELECTOR, 'span.fare').text.strip()
            total_routes = route_element.find_element(By.CSS_SELECTOR, 'span.totalRoutes').text.split()[0]
            first_bus = route_element.find_element(By.XPATH, ".//span[contains(text(), 'First Bus')]//strong").text
            last_bus = route_element.find_element(By.XPATH, ".//span[contains(text(), 'Last Bus')]//strong").text

            data.append({
                'Route': route,
                'Link': link,
                'Fare': fare,
                'Total Routes': total_routes,
                'First Bus': first_bus,
                'Last Bus': last_bus
            })
        except Exception as e:
            logging.error(f"An error occurred while extracting data from the page: {e}")
    
    return data

def extract_data_from_detail_page(driver, link, route):
    driver.get(link)
    wait = WebDriverWait(driver, WAIT_TIME)
    
    try:
        # Ensure the page has loaded
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.bus-items > div')))

        # Scroll down to load more elements
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Reduce the wait time
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Fetch all bus elements
        bus_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.bus-items > div')
        logging.info(f"Number of bus elements found: {len(bus_elements)}")
        extracted_data = []

        for bus_element in bus_elements:
            try:
                # Check if bus element contains the necessary content
                if not bus_element.find_elements(By.CSS_SELECTOR, '.travels'):
                    continue

                # Click on the dropdown for government buses
                if any(gov_bus in bus_element.text for gov_bus in GOV_BUS_NAMES):
                    try:
                        dropdown_button = bus_element.find_element(By.CSS_SELECTOR, '.clearfix.bus-item-details')
                        driver.execute_script("arguments[0].click();", dropdown_button)
                        time.sleep(0.5)  # Reduce the wait time
                    except Exception as e:
                        logging.error(f"An error occurred while clicking the drop-down button: {e}")
                
                operator = bus_element.find_element(By.CSS_SELECTOR, 'div.travels').text
                bus_type = bus_element.find_element(By.CSS_SELECTOR, 'div.bus-type').text
                departure_time = bus_element.find_element(By.CSS_SELECTOR, 'div.dp-time').text
                departure_location = bus_element.find_element(By.CSS_SELECTOR, 'div.dp-loc').get_attribute('title')
                duration = bus_element.find_element(By.CSS_SELECTOR, 'div.dur').text
                arrival_time = bus_element.find_element(By.CSS_SELECTOR, 'div.bp-time').text
                arrival_date = bus_element.find_element(By.CSS_SELECTOR, 'div.next-day-dp-lbl').text if bus_element.find_elements(By.CSS_SELECTOR, 'div.next-day-dp-lbl') else ""
                arrival_location = bus_element.find_element(By.CSS_SELECTOR, 'div.bp-loc').get_attribute('title')
                rating = bus_element.find_element(By.CSS_SELECTOR, 'div.rating span').text if bus_element.find_elements(By.CSS_SELECTOR, 'div.rating span') else ""
                fare = bus_element.find_element(By.CSS_SELECTOR, 'div.fare span').text
                seats_available = bus_element.find_element(By.CSS_SELECTOR, 'div.seat-left').text.split()[0] if bus_element.find_elements(By.CSS_SELECTOR, 'div.seat-left') else ""
                
                data = {
                    'Route': route,
                    'Operator': operator,
                    'Bus Type': bus_type,
                    'Departure Time': departure_time,
                    'Departure Location': departure_location,
                    'Duration': duration,
                    'Arrival Time': arrival_time,
                    'Arrival Date': arrival_date,
                    'Arrival Location': arrival_location,
                    'Rating': rating,
                    'Fare': fare,
                    'Seats Available': seats_available
                }
                extracted_data.append(data)
            except StaleElementReferenceException as e:
                logging.error(f"Stale element reference error while extracting data for one bus: {e}")
            except Exception as e:
                logging.error(f"An error occurred while extracting data for one bus: {e}")
        
        return extracted_data
    except TimeoutException as e:
        logging.error(f"Timeout occurred while waiting for the bus elements: {e}")
    except Exception as e:
        logging.error(f"An error occurred while extracting detail page data: {e}")
    return []

def click_page_tab(driver, page_number):
    retries = 3
    for attempt in range(retries):
        try:
            page_tab = driver.find_element(By.XPATH, f"//div[contains(@class, 'DC_117_pageTabs') and text()='{page_number}']")
            driver.execute_script("arguments[0].scrollIntoView();", page_tab)  # Scroll into view
            time.sleep(1)
            page_tab.click()
            time.sleep(1)  # Reduce the wait time
            return
        except ElementClickInterceptedException:
            logging.warning(f"Attempt {attempt + 1} to click page tab {page_number} failed due to interception.")
            time.sleep(1)  # Reduce the wait time before retrying
        except NoSuchElementException:
            logging.warning(f"Page tab {page_number} not found.")
            return
    logging.error(f"Failed to click page tab {page_number} after {retries} attempts.")

def process_base_url(base_url):
    driver = webdriver.Chrome()
    try:
        all_data = []
        logging.info(f"Processing base URL: {base_url}")
        driver.get(base_url)
        
        # Get total number of pages from the pagination controls
        page_tabs = driver.find_elements(By.CSS_SELECTOR, "div.DC_117_pageTabs")
        total_pages = len(page_tabs)
        logging.info(f"Total pages found: {total_pages}")

        for page_number in range(1, total_pages + 1):
            click_page_tab(driver, page_number)
            page_data = extract_data_from_page(driver)
            logging.info(f"Page {page_number} data extracted: {len(page_data)} records")
            all_data.extend(page_data)

        detailed_data = []
        for data in all_data:
            link = data['Link']
            route = data['Route']
            logging.info(f"Processing route: {route}")
            detail_data = extract_data_from_detail_page(driver, link, route)
            logging.info(f"Details extracted for route {route}: {len(detail_data)} records")
            if detail_data:
                detailed_data.extend(detail_data)

        return detailed_data
    finally:
        driver.quit()

# def main():
all_detailed_data = []
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_base_url, url) for url in BASE_URLS]
    for future in as_completed(futures):
        all_detailed_data.extend(future.result())

detailed_df = pd.DataFrame(all_detailed_data)
logging.info(f"Total detailed records: {len(detailed_df)}")
detailed_df.to_csv("C:/Users/Sai.Vigneshwar/Desktop/detailed_routes_data.csv")
    
    
