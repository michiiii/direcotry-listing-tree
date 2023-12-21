import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the single InsecureRequestWarning from urllib3 needed
warnings.simplefilter('ignore', InsecureRequestWarning)

# ANSI escape codes for text color
BLUE = '\033[94m'
ORANGE = '\033[93m'
RESET = '\033[0m'

def is_directory_listing_page(soup):
    if soup.find('title') and 'Index of' in soup.find('title').get_text():
        return True
    return False

def is_file_based_on_extension(url):
    parsed_url = urlparse(url)
    if '.' in parsed_url.path.split('/')[-1]:
        return True
    return False

def get_file_info(file_url):
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

def fetch_directory_listing(url, soup):
    items = []

    try:
        rows = soup.find_all('tr')
        for row in rows[2:]:
            cols = row.find_all('td')
            if len(cols) > 3:
                name = cols[1].get_text(strip=True)
                if name == 'Parent Directory':
                    continue

                href = cols[1].find('a')['href']
                full_url = urljoin(url, href)
                last_modified = cols[2].get_text(strip=True)

                if is_file_based_on_extension(full_url):
                    size_mb, last_modified = get_file_info(full_url)
                    if isinstance(size_mb, float):
                        details = f"Size: {size_mb:.3f} MB, Last Modified: {last_modified}"
                    else:
                        details = f"Size: {size_mb}, Last Modified: {last_modified}"
                    items.append((False, name, details))
                else:
                    details = f"Last Modified: {last_modified}"
                    items.append((True, name, details))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return items

def print_directory_listing(url, indent=""):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if is_directory_listing_page(soup):
            items = fetch_directory_listing(url, soup)
            items.sort(key=lambda x: (not x[0], x[1]))

            for is_dir, name, details in items:
                if is_dir:
                    print(BLUE + indent + name + RESET)
                    next_url = urljoin(url, name + '/')
                    print_directory_listing(next_url, indent + '    ')
                else:
                    print(ORANGE + indent + f"{name}  {details}" + RESET)
        else:
            print(f"{indent}The page at {url} is not a directory listing. Skipping.")

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and display files in a directory listing URL")
    parser.add_argument("--url", required=True, help="A URL with directory listing")

    args = parser.parse_args()

    print_directory_listing(args.url)

if __name__ == "__main__":
    main()
