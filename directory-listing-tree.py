"""
Directory Listing Script

This script navigates through web server directory listings, prints the content to the console, 
and optionally saves file details (filename, URL, size, and last modified date) to a CSV file.

Usage:
    Run the script with --url to specify the directory listing URL.
    Use --csv to save the results into a CSV file.

Example:
    python directory_listing_tree.py --url "https://example.com/path" --csv

Author: michiiii
Date: 21.12.2023
License: MIT

"""


import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import csv

# Configure warnings and ANSI escape codes for text color
warnings.simplefilter('ignore', InsecureRequestWarning)  # Suppress only the single InsecureRequestWarning from urllib3
BLUE = '\033[94m'
ORANGE = '\033[93m'
RESET = '\033[0m'


def is_directory_listing_page(soup):
    """Check if the BeautifulSoup object represents a directory listing page."""
    return bool(soup.find('title') and 'Index of' in soup.find('title').get_text())


def is_file_based_on_extension(url):
    """Determine if the URL points to a file based on the presence of a file extension."""
    parsed_url = urlparse(url)
    return '.' in parsed_url.path.split('/')[-1]


def get_file_info(file_url):
    """Retrieve file information including size and last modified date."""
    try:
        response = requests.get(file_url, verify=False, stream=True)
        response.raise_for_status()

        file_size_bytes = int(response.headers.get('Content-Length', 0))
        file_size_mb = file_size_bytes / (1024 * 1024)  # Convert to MB

        last_modified = response.headers.get('Last-Modified', None)
        if last_modified:
            try:
                last_modified_date = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
                formatted_last_modified = last_modified_date.strftime('%Y.%m.%d')
            except ValueError:
                formatted_last_modified = "Unknown Date"
        else:
            formatted_last_modified = "Not Available"

        return file_size_mb, formatted_last_modified

    except requests.exceptions.RequestException as e:
        print(f"Error fetching file info for {file_url}: {e}")
        return 'N/A', 'N/A'


def write_to_csv(file_data, csv_filename):
    """Write collected file data into a CSV file."""
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Filename', 'URL', 'Size (MB)', 'Last Modified'])
        writer.writerows(file_data)


def fetch_directory_listing(url, soup, collect_csv=False):
    """Fetch and process the directory listing from the given URL."""
    items = []
    csv_data = []

    try:
        rows = soup.find_all('tr')
        for row in rows[2:]:  # Skip header rows
            cols = row.find_all('td')
            if len(cols) > 3:
                name = cols[1].get_text(strip=True)
                if name == 'Parent Directory':  # Skip 'Parent Directory' entries
                    continue

                href = cols[1].find('a')['href']
                full_url = urljoin(url, href)
                last_modified = cols[2].get_text(strip=True)

                if is_file_based_on_extension(full_url):
                    size_mb, last_modified = get_file_info(full_url)
                    details = f"Size: {size_mb:.3f} MB, Last Modified: {last_modified}"
                    items.append((False, name, details))
                    if collect_csv:
                        csv_data.append([name, full_url, f"{size_mb:.3f}", last_modified])
                else:
                    details = f"Last Modified: {last_modified}"
                    items.append((True, name, details))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return items, csv_data


def print_directory_listing(url, indent="", collect_csv=False):
    """Print the directory listing and return data for CSV if needed."""
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if is_directory_listing_page(soup):
            items, csv_data = fetch_directory_listing(url, soup, collect_csv)
            items.sort(key=lambda x: (not x[0], x[1]))

            for is_dir, name, details in items:
                if is_dir:
                    print(BLUE + indent + name + RESET)
                    next_url = urljoin(url, name + '/')
                    child_csv_data = print_directory_listing(next_url, indent + '    ', collect_csv)
                    if collect_csv:
                        csv_data.extend(child_csv_data)
                else:
                    print(ORANGE + indent + f"{name}  {details}" + RESET)

            return csv_data
        else:
            print(f"{indent}The page at {url} is not a directory listing. Skipping.")

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")


def main():
    """Main function to handle argument parsing and initiate directory listing."""
    parser = argparse.ArgumentParser(description="Fetch and display files in a directory listing URL")
    parser.add_argument("--url", required=True, help="A URL with directory listing")
    parser.add_argument("--csv", action='store_true', help="Also save the results to a CSV file")

    args = parser.parse_args()

    csv_data = print_directory_listing(args.url, collect_csv=args.csv)

    if args.csv and csv_data:
        csv_filename = args.url.replace('http://', '').replace('https://', '').replace('/', '_') + '.csv'
        write_to_csv(csv_data, csv_filename)
        print(f"CSV file created: {csv_filename}")


if __name__ == "__main__":
    main()
