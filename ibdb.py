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
    
    # Debug the HTML content
    logging.debug("HTML Content length: %d", len(html))
    
    # Find all script tags first
    script_tags = bs4.find_all('script')
    logging.debug("Found %d script tags", len(script_tags))
    
    # Look for grossdata in all script tags
    script_tag = None
    for tag in script_tags:
        if tag.string and 'grossdata' in tag.string:
            script_tag = tag
            break

    # Check if the script tag was found
    if script_tag:
        logging.debug("Found script tag with grossdata")
        # Use a regular expression to extract the JSON-like string assigned to 'grossdata'
        match = re.search(r'var\s+grossdata\s*=\s*({.*?});', script_tag.string, re.DOTALL)

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
                logging.debug(f"Problematic JSON string: {json_str}")
        else:
            logging.error("No match found for 'grossdata' in the script content.")
            logging.debug("Script content: %s", script_tag.string[:200] + "...")  # First 200 chars
    else:
        logging.error("Script tag containing 'grossdata' not found in HTML.")
        # Log first 500 characters of HTML for debugging
        logging.debug("HTML preview: %s", html[:500] + "...")

    logging.info("Extracted data:")
    strucrued_data = []
    for key in data.keys():
        logging.debug(f"{key}: {len(data[key])}")
        for row in data[key]:
            try:
                strucrued_data.append({
                    "Week Ending": row[0],
                    "Gross": row[6],
                    "Attendance": row[7],
                    "% Capacity": row[8],
                    "# Previews": row[9],
                    "# Perf.": row[10],
                })
            except IndexError as e:
                logging.error(f"Error processing row {row}: {e}")

    # Return the extracted data
    logging.debug(strucrued_data)
    return strucrued_data

# Example usage:
# html_content = ...  # Load your HTML content here
# gross_data = etl(html_content)
# print(gross_data)