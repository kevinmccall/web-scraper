from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
import os
import sys
import shutil
import re


URL_MAIN = "https://www.nchsaa.org/news/2022-10-20/2022-volleyball-final-rpi-rankings"
OUTPUT_FILE = "urls.txt"


def get_volleyball_urls():
    print("THIS TAKES A WHILE")
    url_regex = re.compile(r"(.+\/)")
    # Saves a copy of the last urls saved
    if os.path.exists(OUTPUT_FILE):
        shutil.copyfile(OUTPUT_FILE, OUTPUT_FILE + ".old")
    with open(OUTPUT_FILE, "w", encoding="utf8") as writer:
        # Opens up the main url and scrapes the links from the table
        try:
            main_response = requests.get(URL_MAIN)
        except ConnectionError:
            print(f"Unable to establish connection with {URL_MAIN}")
            sys.exit()
        if main_response.ok:
            soup = BeautifulSoup(main_response.content, "html.parser")
            tables = soup.find_all("table")
            for table in tables:
                for row_index, table_row in enumerate(table.find_all("tr")):
                    link = table_row.find("a")
                    if link:
                        try:
                            # Get url for the schedule website
                            schedule_url = requests.get(link.get("href")).url
                            schedule_url = (
                                url_regex.search(schedule_url).group(1) + "schedule"
                            )
                            schedule_response = requests.get(schedule_url)
                            if schedule_response.ok:
                                soup2 = BeautifulSoup(
                                    schedule_response.content, "html.parser"
                                )
                                secondary_link = soup2.find("a", string="Print")
                                if secondary_link:
                                    desired_url = secondary_link.get("href")
                                else:
                                    print(
                                        f"Error finding the print button on the webpage {schedule_response.url}? skipping..."
                                    )
                                    continue
                                if desired_url:
                                    writer.write(desired_url + "\n")
                                else:
                                    print(
                                        f"Error extracting URL from {link.get_text()}"
                                    )
                            else:
                                print(
                                    f"Error getting the schedule website for {link.get_text()}: {schedule_url}"
                                )
                        except ConnectionError:
                            print(
                                f"Website would not connect, skipping...: {link.get('href')}"
                            )
                            continue
                    else:
                        print(
                            f"Error getting website link off of table. (row {row_index})"
                        )
        else:
            print(f"Error accessing webpage: {URL_MAIN}")


def main():
    get_volleyball_urls()


if __name__ == "__main__":
    main()
