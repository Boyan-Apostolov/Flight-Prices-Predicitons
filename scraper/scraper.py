"""
Google Flights Price Scraper using Playwright

This script automates flight price scraping from Google Flights and exports data to CSV.

Author: Boyan Apostolov
GitHub: github.com/Boyan-Apostolov/Flight-Prices-Predicitons
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import requests
import re
import csv
import random

public_holidays_endpoint = "https://openholidaysapi.org/PublicHolidays?countryIsoCode=BG&countryIsoCode=NL&languageIsoCode=EN&validFrom=2025-01-01&validTo=2025-12-31"

school_holidays_endpoint = "https://openholidaysapi.org/SchoolHolidays?countryIsoCode=NL&validFrom=2025-01-01&validTo=2025-12-31"

today = datetime.today()
data = []

public_holidays_data = []
school_holidays_data = []
all_holidays_data = []


def get_near_holiday_status(departure_date, holidays):
    for holiday in holidays:
        holiday_date = datetime.strptime(holiday, "%Y-%m-%d")
        if departure_date == holiday_date:
            return 0  # During the holiday
        elif departure_date >= holiday_date - timedelta(days=7) and departure_date < holiday_date:
            return -1  # 1 week before the holiday
        elif departure_date > holiday_date and departure_date <= holiday_date + timedelta(days=7):
            return 1  # 1 week after the holiday
    return None  # Not near a holiday


def get_random_airline():
    return random.choices(
        ["Delta", "Republic American", "Other"],
        weights=[0.6, 0.3, 0.1]
    )[0]


def extract_number(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0


def get_date_range(start_date: str, end_date: str):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]


def parse_holidays(url, holiday_list):
    response = requests.get(url)
    if response.status_code == 200:
        holidays = response.json()
        for holiday in holidays:
            holiday_list.extend(get_date_range(
                holiday['startDate'], holiday['endDate']))
    else:
        print(
            f"❌ Failed to fetch data from API. Status code: {response.status_code}")


def preload_holidays():
    global public_holidays_endpoint, school_holidays_endpoint, public_holidays_data, school_holidays_data, all_holidays_data

    print("\n🚀 Fetching holidays...\n")

    public_holidays_data.clear()
    school_holidays_data.clear()

    parse_holidays(public_holidays_endpoint, public_holidays_data)
    parse_holidays(school_holidays_endpoint, school_holidays_data)

    all_holidays_data = list(set(public_holidays_data + school_holidays_data))

    print("Public and School Holiday loaded successfully")


def export_to_csv(data, filename="flight_prices_JFK_DCA.csv"):
    if not data:
        print("❌ No data to export.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Data successfully exported to {filename}")


def open_webpage(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = open_flights(browser, url)

        print("\n🚀 Flights scraper started...\n")

        for i in range(200):  # To adjust the future days count
            scrape_page(page)
            next_date(page)
            page.wait_for_timeout(200)

        print("\n✅ Flights scraper finished!\n")
        print(f"📊 Total data collected: {len(data)} records")

        export_to_csv(data)
        browser.close()


def scrape_page(page):
    try:
        # Get the departure and arrival airports
        departure_airport = page.locator(
            ".V00Bye.ESCxub.KckZb input").nth(0).input_value()
        arrival_airport = page.locator(
            ".V00Bye.ESCxub.KckZb input").nth(1).input_value()

        # Get the departure date input value
        departure_date_input = page.locator(
            ".TP4Lpb.eoY5cb.j0Ppje").nth(0).input_value()
        departure_date = datetime.strptime(
            departure_date_input + ", 2025", "%a, %b %d, %Y")
        departure_date_formatted = departure_date.strftime("%Y-%m-%d")

        print(f"📅 Scraping for - Departure date: {departure_date_formatted}")

        # Check if "View price history" button is available
        page.wait_for_selector(":has-text('View price history')", timeout=1000)

        page.click(".vx1PSc")  # Expanding the history so it can load the data

        history_point_marker = ".ke9kZe-LkdAo-RbRzK-JNdkSc"
        page.wait_for_selector(history_point_marker, timeout=1000)
        elements = page.locator(history_point_marker).all()

        for element in elements:
            aria_label = element.get_attribute("aria-label") or ""

            # Extracting "days ago" and price
            parts = aria_label.split(" ")
            history_days_ago = 0 if parts[0] == "Today" else int(
                parts[0]) if parts[0].isdigit() else 0

            price = parts[-1].split(" ")[-1] if len(parts) > 1 else "N/A"
            price = extract_number(price)
            # Calculate absolute days before departure
            days_ago = abs((departure_date - today).days) + history_days_ago

            departure_date_obj = datetime.strptime(
                departure_date_formatted, "%Y-%m-%d")

            near_holiday = get_near_holiday_status(
                departure_date_obj, all_holidays_data)

            record_timestamp = (departure_date_obj -
                                timedelta(days=days_ago)).strftime("%Y-%m-%d")

            entry = {
                "daysAgo": days_ago,
                "departureDate": departure_date_formatted,
                "price": price,
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "is_public_holiday": departure_date_formatted in public_holidays_data,
                "is_school_holiday": departure_date_formatted in school_holidays_data,
                "airline": get_random_airline(),
                "near_holiday": near_holiday,
                "record_timestamp": record_timestamp
            }
            data.append(entry)

    except Exception as e:
        print(
            f"❌ No flights for: {departure_date_formatted}, going to next day. Error: {e}")


def open_flights(browser, url):
    page = browser.new_page()
    page.goto(url)

    print(f"🌍 Opened {url} successfully!")

    # Wait for and click the "Accept all" cookies button
    page.wait_for_selector("button:has-text('Accept all')", timeout=1000)
    page.click("button:has-text('Accept all')")
    print("✅ Clicked the 'Accept all' button!")

    return page


def next_date(page):
    try:
        # Wait for date picker to be available
        page.wait_for_selector(".VfPpkd-Jh9lGc")
        date_picker = page.locator(".BLohnc.q5Vmde").first

        date_picker.click()
        page.wait_for_timeout(200)
        date_picker.press("ArrowRight")
        date_picker.press("Enter")

        print("➡️ Moved to the next date")
        page.wait_for_timeout(200)

    except Exception as e:
        print(f"⚠️ Error navigating to the next date: {e}")


if __name__ == "__main__":
    preload_holidays()

    open_webpage("https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI1LTAzLTI0agcIARIDSkZLcgwIAxIIL20vMHJoNmtAAUgBcAGCAQsI____________AZgBAg&curr=EUR")
