import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
from datetime import datetime
import time

# ANSI escape codes for text color
BLUE = '\033[94m'
ORANGE = '\033[93m'
RESET = '\033[0m'

def is_directory_listing_link(link):
    # Check if the link ends with '/' indicating it's a directory
    return link.endswith('/')

def extract_directory_name(link_text):
    # Extract the directory name from the link text
    return link_text.strip('/')

def get_file_info(file_url):
    try:
        response = requests.head(file_url)
        response.raise_for_status()
        
        # Extract file size and convert it to MB
        file_size_bytes = int(response.headers.get('Content-Length', '0'))
        file_size_mb = file_size_bytes / (1024 * 1024)  # Convert to MB
        
        # Format the last modified date as yyyy.mm.dd
        last_modified = response.headers.get('Last-Modified', 'N/A')
        last_modified_date = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        formatted_last_modified = last_modified_date.strftime('%Y.%m.%d')

        return file_size_mb, formatted_last_modified

    except requests.exceptions.RequestException as e:
        print(f"Error fetching file info for {file_url}: {e}")
        return 'N/A', 'N/A'

def fetch_directory_listing(url, indent=""):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        parent_directory_found = False

        for link in soup.find_all('a', href=True):
            href = link['href']
            directory_name = extract_directory_name(link.get_text())

            if parent_directory_found:
                if is_directory_listing_link(href):
                    # It's a directory (blue text)
                    print(BLUE + indent + directory_name + RESET)
                    fetch_directory_listing(urljoin(url, href), indent + '  ')
                else:
                    # It's a file (orange text)
                    file_url = urljoin(url, href)
                    file_size_mb, last_modified = get_file_info(file_url)
                    print(ORANGE + indent + f"{directory_name}  Size: {file_size_mb:.2f} MB, Last Modified: {last_modified}" + RESET)

            elif directory_name == 'Parent Directory':
                # Found the "Parent directory" link
                parent_directory_found = True

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and display files in a directory listing URL")
    parser.add_argument("--url", required=True, help="A URL with directory listing")

    args = parser.parse_args()

    url = args.url
    fetch_directory_listing(url)

if __name__ == "__main__":
    main()
