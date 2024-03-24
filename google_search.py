from serpapi import GoogleSearch
from dotenv import load_dotenv
import csv
import os

load_dotenv("api_keys.env")
api_key = os.getenv("SERPAPI_GOOGLE_SEARCH_KEY")

# Prompt the user for search query and date range
search_query = input("Enter your search query: ")
start_date = input("Enter the start date (format m/d/yyyy): ")
end_date = input("Enter the end date (format m/d/yyyy): ")
date_range = f"{start_date}-{end_date}"

# Set up the search parameters with user inputs
params = {
  "engine": "google",
  "q": search_query,
  "api_key": api_key,
  "google_domain": "google.com",
  "gl": "us",
  "hl": "en",
  "tbs": f"cdr:1,cd_min:{start_date},cd_max:{end_date}",
  "sort": "date"
}

# Create a GoogleSearch object with the parameters
search = GoogleSearch(params)

# Get the search results as a dictionary
results = search.get_dict()

# Extract the organic search results
organic_results = results["organic_results"]

# Print the organic search results
for result in organic_results:
    print(result['title'], "-", result['link'])

def export_to_csv(organic_results, filename, search_params):
    """
    Export organic search results to a CSV file, including the publication date and search parameters.

    Parameters:
        organic_results (list): List of dictionaries containing organic search results.
        filename (str): Name of the CSV file to export the results to.
        search_params (dict): Dictionary containing the search parameters.
    """
    # Get the path to the desktop directory
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Define the full path to the CSV file on the desktop
    file_path = os.path.join(desktop_path, filename)

    # Open the file for writing
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write search parameters (metadata) at the top
        writer.writerow(['Search Query Parameters'])
        for key, value in search_params.items():
            writer.writerow([key, value])
        writer.writerow([])  # Add a blank row for separation

        # Now, switch to writing the search results
        fieldnames = ["Title", "Link", "Date"]
        dict_writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header row for search results
        dict_writer.writeheader()

        # Write each organic search result as a row in the CSV file
        for result in organic_results:
            dict_writer.writerow({
                "Title": result.get("title", " "),
                "Link": result.get("link", ""),
                "Date": result.get("date", "N/A")  # Use the publication date if available
            })

    print(f"Organic search results have been exported to {file_path}")


export_to_csv(organic_results, "organic_results.csv", params)
