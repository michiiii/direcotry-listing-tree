# Directory Listing Script

## Overview
This Python script navigates through web server directory listings and optionally saves file details to a CSV file. It's designed to work with directory listings that follow a specific HTML structure typically found on web servers.

## Features
- Navigates through directory listings recursively.
- Prints directory and file details to the console.
- Optionally outputs file details (filename, URL, size, and last modified date) to a CSV file.

## Requirements
- Python 3.x
- `requests` library
- `beautifulsoup4` library

## Installation
Before running the script, ensure you have Python installed and then install the required Python packages:

```bash
pip install requests beautifulsoup4
```

## Usage
Run the script from the command line, providing the URL of the directory listing:

```bash
python directory_listing_tree.py --url "https://example.com/path/to/directory"
```

To also save the results to a CSV file, add the `--csv` flag:

```bash
python directory_listing_tree.py --url "https://example.com/path/to/directory" --csv
```

![image](https://github.com/michiiii/directory-listing-tree/assets/12173974/8043cf17-d3c4-4ecc-a14e-7df41f129823)


The CSV file will be named after the URL with slashes replaced by underscores.

## Cautionary Notes
- This script disables SSL warnings. Use it only on trusted sites and understand the security implications.
- Ensure the URL provided does not contain any sensitive or private information, as it's used in the CSV filename.
- The script assumes a specific HTML structure for the directory listings. It may require adjustments for other structures.
- Always test the script in a controlled environment before use.

## Contributing
Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/michiiii/directory-listing-tree/issues) if you want to contribute.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contact
Michael Ritter – [@BigM1ke_oNe](https://twitter.com/BigM1ke_oNe)
