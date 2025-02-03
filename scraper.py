import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin  # For handling relative URLs

# Base URL of the UT Austin calendar
base_url = "https://calendar.utexas.edu/calendar"

# List to hold all event data
event_data = []

# Start with the first page
current_url = base_url

while True:
    # Send a GET request to the current URL
    response = requests.get(current_url)

    if response.status_code != 200:
        print(f"Failed to retrieve data from {current_url}: {response.status_code}")
        break

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all events
    events = soup.find_all("div", class_="em-card")

    # Extract data from each event
    for event in events:
        title = event.find("h3").text.strip()
        event_texts = event.find_all("p", class_="em-card_event-text")

        date_time = event_texts[0].text.strip() if len(event_texts) > 0 else None
        location = event_texts[1].text.strip() if len(event_texts) > 1 else None
        link = event.find("a")["href"]
        image_url = event.find("img")["src"] if event.find("img") else None

        event_data.append(
            {
                "Title": title,
                "Date/Time": date_time,
                "Location": location,
                "Event Link": link,
                "Image URL": image_url,
            }
        )

    # Check for pagination
    pagination = soup.find("ul", class_="em-search-pagination")
    if not pagination:
        break  # No pagination found

    # Find the "Next" button (last <li> in pagination)
    next_button_li = pagination.find_all("li")[-1]
    next_button = next_button_li.find("a") or next_button_li.find("div")

    # Stop if the "Next" button is disabled
    if "disabled" in next_button.get("class", []):
        break

    # Get the next page URL if available
    next_page_link = next_button_li.find("a")
    if next_page_link and "href" in next_page_link.attrs:
        current_url = urljoin(base_url, next_page_link["href"])
    else:
        break  # No valid next page link

# Create DataFrame and save to CSV
if event_data:
    df = pd.DataFrame(event_data)

    # Ensure the 'data' directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    df.to_csv("data/ut_austin_events.csv", index=False)
    print("Data successfully scraped and saved to data/ut_austin_events.csv")
else:
    print("No events found to scrape")
