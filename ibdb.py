import re
import json
from bs4 import BeautifulSoup
import logging

def etl(html):
    # Initialize an empty dictionary to store the extracted data
    data = {}

    # Log the start of the extraction process
    logging.info("Extracting data from IBDB")

    # Parse the HTML content with BeautifulSoup
    bs4 = BeautifulSoup(html, 'html.parser')

    # Find the script tag that contains the 'grossdata' variable
    script_tag = bs4.find('script', string=re.compile(r'var grossdata ='))

    # Check if the script tag was found
    if script_tag:
        # Use a regular expression to extract the JSON-like string assigned to 'grossdata'
        match = re.search(r'var grossdata = ({.*?});', script_tag.string, re.DOTALL)

        if match:
            # Extract the JSON-like string
            json_str = match.group(1)

            # Attempt to convert the JavaScript object to valid JSON
            # Add double quotes around property names
            json_str = re.sub(r'([{,])(\s*)([A-Za-z0-9_]+?)\s*:', r'\1"\3":', json_str)
            # Replace single quotes with double quotes around string values
            json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)

            try:
                # replace all single quotes with double quotes
                json_str = json_str.replace("'", '"')

                # Parse the JSON string into a Python dictionary
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON: {e}")
        else:
            logging.error("No match found for 'grossdata' in the script content.")
    else:
        logging.error("Script tag containing 'grossdata' not found in HTML.")

    logging.info("Extracted data:")
    strucrued_data = []
    for key in data.keys():
        logging.debug(f"{key}: {len(data[key])}")
        for row in data[key]:
            logging.debug(row)
            strucrued_data.append({
                "Week Ending": row[0],
                "Gross": row[6],
                "Attendance": row[7],
                "% Capacity": row[8],
                "# Previews": row[9],
                "# Perf.": row[10],
            })

    # Return the extracted data
    logging.debug(strucrued_data)
    return strucrued_data

# Example usage:
# html_content = ...  # Load your HTML content here
# gross_data = etl(html_content)
# print(gross_data)