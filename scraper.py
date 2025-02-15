"""
Google Flights Price Scraper using Playwright

This script automates flight price scraping from Google Flights and exports data to CSV.

Author: Boyan Apostolov
GitHub: github.com/Boyan-Apostolov/Flight-Prices-Predicitons
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import csv

today = datetime.today()
data = []


def export_to_csv(data, filename="flight_prices.csv"):
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
        browser = p.chromium.launch(headless=False)
        page = open_flights(browser, url)

        print("\n🚀 Flights scraper started...\n")

        for i in range(319):  # Adjust as needed
            print(f"🔄 Scraping iteration {i+1}/319...")
            scrape_page(page)
            next_date(page)
            page.wait_for_timeout(200)

        print("\n✅ Flights scraper finished!\n")
        print(f"📊 Total data collected: {len(data)} records")

        export_to_csv(data)
        browser.close()


def scrape_page(page):
    try:
        # Get the departure date input value
        departure_date_input = page.locator(
            ".TP4Lpb.eoY5cb.j0Ppje").nth(0).input_value()
        departure_date = datetime.strptime(
            departure_date_input, "%a, %b %d").replace(year=2025)
        departure_date_formatted = departure_date.strftime("%d-%m-%Y")

        print(f"📅 Scraping for - Departure date: {departure_date_formatted}")

        # Check if "View price history" button is available
        page.wait_for_selector(":has-text('View price history')", timeout=1000)
        page.click(":has-text('View price history')")

        # Get all history points
        history_point_marker = ".ke9kZe-LkdAo-RbRzK-JNdkSc"
        page.wait_for_selector(history_point_marker)
        elements = page.locator(history_point_marker).all()

        for element in elements:
            aria_label = element.get_attribute("aria-label") or ""

            # Extracting "days ago" and price
            parts = aria_label.split(" ")
            history_days_ago = 0 if parts[0] == "Today" else int(
                parts[0]) if parts[0].isdigit() else 0
            price = parts[-1] if len(parts) > 1 else "N/A"

            # Calculate absolute days ago
            days_ago = abs((departure_date - today).days) + history_days_ago

            entry = {
                "daysAgo": days_ago,
                "departureDate": departure_date_formatted,
                "price": price
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
    open_webpage("https://www.google.com/travel/flights/search?tfs=CBwQAhogEgoyMDI1LTAyLTE1KABqBwgBEgNFSU5yBwgBEgNTT0ZAAUgBcAGCAQsI____________AZgBAg&tfu=EgoIABAAGAAgASgC")
